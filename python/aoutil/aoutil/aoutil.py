import aolog
import  hashlib


def delta_sync():
    pass

def detect_deltas(collection1: list|dict, collection2: list|dict, lookupKey: str|None) -> tuple[aolog.AoLog, dict]:
    Log = aolog.AoLog()
    
    if isinstance(collection1, list) and isinstance(collection2, list):
        greaterLength = max(len(collection1), len(collection2))
        lengthDifference = len(collection1) - len(collection2)
        deltaIndicies = []
        errorIndicies = []
        for i in range(greaterLength):
            InnerLog, areSame = row_hash_comparison(collection1[i], collection2[i])
            Log.rollup_aolog(InnerLog)

            if Log.has_errors:
                errorIndicies.append(i)
                continue
            
            elif areSame:
                deltaIndicies.append(i)
                continue
            
            else:
                continue





    

def row_hash_comparison(row1: dict|list, row2: dict|list) -> tuple[aolog.AoLog, bool]:
    Log = aolog.AoLog()
    areSame = False

    if isinstance(row1, list) and isinstance(row2, list):
        if len(row1) != len(row2):
            Log.log_warning(f"list length mismatch", f"len(row1) = {len(row1)} - len(row2) = {len(row2)}")
            pass
        
        else:
            try:
                hashableRow1= str(enumerate(sorted(row1))).encode()
                hashableRow2= str(enumerate(sorted(row2))).encode()

                if hashlib.sha256(hashableRow1) == hashlib.sha256(hashableRow2):
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

                if hashlib.sha256(hashableDict1) == hashlib.sha256(hashableDict2):
                    areSame = True
            
            except Exception as e:
                Log.log_error(f"failed to hash either row1 or row2. all row values must be hashable types", str(e))

            else:
                pass
    
    else:
        Log.log_error(f"incorrect types for row1 and/or row2. must be list or dict", f"type(row1) = {type(row1)} - type(row2) = {type(row2)}")

    return Log, areSame