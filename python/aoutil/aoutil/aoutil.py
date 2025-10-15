import aolog
import  hashlib, datetime


def delta_sync(collection1: list|dict, collection2: list|dict, source_of_truth: int = 0, error_threshold: int = 10) -> tuple[aolog.AoLog, int]:
    Log = aolog.AoLog()
    changesMade = 0
    InnerLog, errors, deltas = detect_deltas(collection1=collection1, collection2=collection2, error_threshold=error_threshold)
    Log.rollup_aolog(InnerLog)

    if Log.has_errors:
        pass

    else:
        pass

    return Log, changesMade
        
        
    

def ajudicate_changes(collection1, collection2, deltas: list, use_updated: bool, source_of_truth: int) -> tuple[aolog.AoLog, list|dict]:
    Log = aolog.AoLog()

    if use_updated:
        if not isinstance(collection1, dict) or not isinstance(collection2, dict):
            Log.log_error(f"both 'collection1' and 'collection2' must be dicts in order to use the 'use_updated' param.", f"Provided types: collection1: {type(collection1)} -- collection2: {type(collection2)}")
            pass

        else:
            ancientTime = datetime.datetime(2000, 1, 1)
            for key in deltas:
                col1Updated = collection1.get(key,{"updated": ancientTime}).get("updated", ancientTime) for key in deltas}
                col2Updated = {key: collection2.get(key,{"updated": ancientTime}).get("updated", ancientTime) for key in deltas}
            
            updatedComparision = tuple(zip(col1Updated, col2Updated)) 

            updates = []
            errors = []
            for datePair in updatedComparision:
                if not isinstance(datePair[0], datetime.datetime) or not isinstance(datePair[1], datetime.datetime):
                    Log.log_error(f"The values of the updated keys must be datetime.datetim objects. No decision will be made for this key", f"provided types: {type(datePair[0])} -- {type(datePair[1])}")
                    errors.append()

                if datePair[0]

            updates = map(lambda x: 0 if x[0] > x[1] else 1, updatedComparision)



    elif isinstance(collection1, list) and isinstance(collection2, list):
        if source_of_truth == 0:
            for index in deltas:
                collection1[index]
        
    

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