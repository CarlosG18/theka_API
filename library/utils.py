def validar_isbn10(isbn):
    """Valida o dígito verificador do ISBN-10"""
    if len(isbn) != 10:
        return False
    
    total = 0
    for i in range(9):
        total += int(isbn[i]) * (10 - i)
    
    digito_verificador = isbn[9]
    if digito_verificador == 'X':
        total += 10
    else:
        total += int(digito_verificador)
    
    return total % 11 == 0

def validar_isbn13(isbn):
    """Valida o dígito verificador do ISBN-13"""
    if len(isbn) != 13:
        return False
    
    total = 0
    for i in range(12):
        if i % 2 == 0:
            total += int(isbn[i])
        else:
            total += int(isbn[i]) * 3
    
    digito_verificador = (10 - (total % 10)) % 10
    return digito_verificador == int(isbn[12])