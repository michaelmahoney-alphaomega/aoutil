import aolog
import  hashlib, datetime


def delta_sync(
    collection1: list|dict, 
    collection2: list|dict, 
    source_of_truth: int = 0, 
    use_updated: bool = False, 
    error_threshold: int = 10, 
    commit_changes: bool = True
) -> tuple[aolog.AoLog, dict]:
    """
    """

    Log = aolog.AoLog()

    InnerLog, errors, deltas = detect_deltas(collection1=collection1, collection2=collection2, error_threshold=error_threshold)
    Log.rollup_aolog(InnerLog)
    
    deltasActual = []
    for i in deltas:
        deltasActual.append((i, collection1[i], collection2[i]))
    
    InnerLog, changes = adjudicate_changes(
        deltas = deltasActual, 
        use_updated = use_updated, 
        source_of_truth = source_of_truth,
    )
    
    if commit_changes:
        for key, value in changes:
            collection1[key] = value
    
    else:
        pass

    return Log, changes
        

        
def adjudicate_changes(deltas: list[tuple], use_updated: bool, source_of_truth: int) -> tuple[aolog.AoLog, dict]:
    Log = aolog.AoLog()
    changes = {}

    if use_updated:
        if not isinstance(deltas[0][1], dict) or not isinstance(deltas[0][2], dict):
            Log.log_error(f"both 'collection1' and 'collection2' must be dicts in order to use the 'use_updated' param.", f"Provided types: collection1: {type(collection1)} -- collection2: {type(collection2)}")
            pass

        else:
            ancientTime = datetime.datetime(2000, 1, 1)
            for change_row in deltas:
                key = change_row[0]
                row1 = change_row[1]
                row2 = change_row[2]

                row1Updated = row1.get("updated", ancientTime)
                row2Updated = row2.get("updated", ancientTime)
                
                if row1Updated >= row2Updated:
                    changes[key] = row1
                
                elif row1Updated < row2Updated:
                    changes[key] = row2
                
                else:
                    Log.log_error(f"something went wrong when trying to compare the updated fields from the collections. Going with the default source of truth.", f"Time1: {row1Updated} -- Time2: {row2Updated}")
                    if source_of_truth == 1:
                        changes[key] = row1
                    
                    elif source_of_truth == 2:
                        changes[key] = row2
                    
                    else:
                        pass

    elif isinstance(deltas[0][1], dict) and isinstance(deltas[0][2], dict):
        for change_row in deltas:
            key = change_row[0]
            row1 = change_row[1]
            row2 = change_row[2]

            if source_of_truth == 1:
                changes[key] = row1
            
            elif source_of_truth == 2:
                changes[key] = row2
            
            else:
                pass
            
    elif isinstance(deltas[0][1], list) and isinstance(deltas[0][2], list):
        for change_row in deltas:
            key = change_row[0]
            row1 = change_row[1]
            row2 = change_row[2]

            if source_of_truth == 1:
                changes[key] = row1
            
            elif source_of_truth == 2:
                changes[key] = row2
            
            else:
                pass
            
    else:
        Log.log_error(f"improper types for collection1 and collection2. They must be both dics or lists.", f"Type collection1: {type()}")
    
    return Log, changes

def detect_deltas(collection1: list|dict, collection2: list|dict, error_threshold: int = 10) -> tuple[aolog.AoLog, list, list]:
    Log = aolog.AoLog()
    deltas = []
    errors = []
    
    if isinstance(collection1, list) and isinstance(collection2, list):
        greaterLength = max(len(collection1), len(collection2))
        lesserLength = min(len(collection1), len(collection2))
        lengthDifference = greaterLength - lesserLength
        for i in range(lesserLength):
            Log.reset_errors()
            
            InnerLog, areSame = row_hash_comparison(collection1[i], collection2[i])
            Log.rollup_aolog(InnerLog)

            if Log.has_errors:
                errors.append(i)
                continue
            
            elif not areSame:
                deltas.append(i)
                continue
            
            else:
                continue
        
        try:
            deltas.append(collection1[lesserLength:greaterLength])
        
        except Exception as e:
            deltas.append(collection2[lesserLength:greaterLength])
        
        Log.log_info(f"There were {len(deltas)} deltas detected - {lengthDifference} elements from the size differences of the lists")

        if len(errors) > error_threshold:
            Log.log_error(f"There were {len(errors)} errors detected. This is more than the provided threshold: {error_threshold}", "")
        
    elif isinstance(collection1, dict) and isinstance(collection2, dict):
        c1Keys = set(collection1.keys())
        c2Keys = set(collection2.keys())
        allKeys = c1Keys.union(c2Keys)
        uniqueKeys = c1Keys.symmetric_difference(c2Keys)
        
        deltas.append(uniqueKeys)

        for key in allKeys.difference(uniqueKeys):
            Log.reset_errors() # reset to make detection of new errors easier.

            InnerLog, areSame = row_hash_comparison(row1=collection1[key], row2 = collection2[key])
            print(areSame)
            Log.rollup_aolog(InnerLog)

            if Log.has_errors:
                errors.append(key)
                continue
            
            elif not areSame:
                deltas.append(key)
                continue
            
            else:
                continue

        Log.log_info(f"There were {len(deltas)} deltas detected - {len(uniqueKeys)} keys from the number of keys unique to either list.")

        if len(errors) > error_threshold:
            Log.log_error(f"There were {len(errors)} errors detected. This is more than the provided threshold: {error_threshold}", "")
    
    else:
        Log.log_error(f"Collection1 and collection 2 must be either lists or dicts and must be of the same type.", f"collection1 type: {type(collection1)} - collection2 type: {type(collection2)}")
            
    return Log, errors, deltas
        
def row_hash_comparison(row1: dict|list, row2: dict|list) -> tuple[aolog.AoLog, bool]:
    Log = aolog.AoLog()
    areSame = False

    if isinstance(row1, list) and isinstance(row2, list):
        if len(row1) != len(row2):
            Log.log_warning(f"list length mismatch", f"len(row1) = {len(row1)} - len(row2) = {len(row2)}")
            pass
        
        else:
            try:
                hashableRow1= str(row1).encode()
                hashableRow2= str(row2).encode()

                if hashlib.sha256(hashableRow1).hexdigest() == hashlib.sha256(hashableRow2).hexdigest():
                    areSame = True
            
            except Exception as e:
                Log.log_error(f"failed to hash either row1 or row2. all row values must be hashable types", str(e))
            
    elif isinstance(row1, dict) and isinstance(row2, dict):
        row1Keys = set(row1.keys())
        row2Keys = set(row2.keys())

        if row1Keys != row2Keys:
            row1MissingKeys = row1Keys - row2Keys
            row2MissingKeys = row2Keys - row1Keys
            Log.log_warning(f"dictionary key mismatch.", f"keys missing from row1: {row1MissingKeys} - keys missing from row2: {row2MissingKeys}")
            pass

        else:
            try:
                hashableDict1 = str(sorted(tuple(row1))).encode()
                hashableDict2 = str(sorted(tuple(row2))).encode()

                if hashlib.sha256(hashableDict1).hexdigest() == hashlib.sha256(hashableDict2).hexdigest():
                    areSame = True
            
            except Exception as e:
                Log.log_error(f"failed to hash either row1 or row2. all row values must be hashable types", str(e))

            else:
                pass
    
    else:
        Log.log_error(f"incorrect types for row1 and/or row2. must be list or dict", f"type(row1) = {type(row1)} - type(row2) = {type(row2)}")

    return Log, areSame