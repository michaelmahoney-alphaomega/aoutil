import aolog
import  hashlib


def delta_sync():
    pass

def detect_deltas(collection1: list|dict, collection2: list|dict, lookupKey: str|None, error_threshold: int = 10) -> tuple[aolog.AoLog, list, list]:
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