def code(code_id, pronombre):
    code = 0;
    if code_id is None:
        code = 1
        codigo = f"{pronombre}0001"
    else:
        code = code_id+1
    #ESTU0001    
    if code < 10:
        codigo = f"{pronombre}000{code}"
    elif code < 100:
    #ESTU099
        codigo = f"{pronombre}00{code}"
    #ESTU999
    elif code < 1000:
        codigo = f"{pronombre}0{code}" 
    else:
        codigo = f"{pronombre}{code}" 
        
    return codigo 


        
"""
if __name__ == "__main__":
    code_id = input("De el Id de Alumno ")
    pronombre = input("De el pronombre que acompañara al codigo ")
    print(code(int(code_id),pronombre))
"""