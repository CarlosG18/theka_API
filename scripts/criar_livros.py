"""
Cria os livros de scripts/livros.json na Theka API via HTTP.

Uso:
    python scripts/criar_livros.py                          # produção
    python scripts/criar_livros.py http://localhost:8000    # local

Gêneros e editoras são informados por nome no JSON; os que não existirem são criados.
Livros cujo ISBN já existe são ignorados, então o script pode ser rodado de novo.
"""
import json
import sys
import uuid
import urllib.error
import urllib.request
from pathlib import Path

BASE_URL = (sys.argv[1] if len(sys.argv) > 1 else "https://thekaapitrainee1.pythonanywhere.com").rstrip("/")
PASTA = Path(__file__).parent


def requisicao(metodo, caminho, corpo=None, content_type=None):
    req = urllib.request.Request(f"{BASE_URL}{caminho}", data=corpo, method=metodo)
    if content_type:
        req.add_header("Content-Type", content_type)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, json.loads(resp.read() or "null")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")


def multipart(campos, arquivo=None):
    """Monta um corpo multipart/form-data com os campos e, opcionalmente, a capa."""
    boundary = uuid.uuid4().hex
    partes = []
    for nome, valor in campos.items():
        partes.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{nome}"\r\n\r\n{valor}\r\n'.encode())
    if arquivo:
        partes.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="capa"; filename="{arquivo.name}"\r\n'
            f"Content-Type: image/jpeg\r\n\r\n".encode() + arquivo.read_bytes() + b"\r\n"
        )
    partes.append(f"--{boundary}--\r\n".encode())
    return b"".join(partes), f"multipart/form-data; boundary={boundary}"


def id_por_nome(recurso, nome, cache):
    """Retorna o id do gênero/editora com esse nome, criando-o se não existir."""
    if not cache:
        status, dados = requisicao("GET", f"/{recurso}/")
        if status != 200:
            sys.exit(f"Erro ao listar /{recurso}/ ({status}): {dados}")
        cache.update({item["nome"].lower(): item["id"] for item in dados})
    if nome.lower() not in cache:
        status, dados = requisicao("POST", f"/{recurso}/", json.dumps({"nome": nome}).encode(), "application/json")
        if status != 201:
            sys.exit(f"Erro ao criar {recurso[:-1]} '{nome}' ({status}): {dados}")
        cache[nome.lower()] = dados["id"]
    return cache[nome.lower()]


def isbn_existe(isbn):
    status, dados = requisicao("GET", f"/livros/?search={isbn}")
    return status == 200 and any(livro["isbn"] == isbn for livro in dados["results"])


def main():
    livros = json.loads((PASTA / "livros.json").read_text(encoding="utf-8"))
    generos, editoras = {}, {}
    criados = ignorados = erros = 0

    for livro in livros:
        if isbn_existe(livro["isbn"]):
            print(f"= já existe: {livro['titulo']}")
            ignorados += 1
            continue

        campos = {k: v for k, v in livro.items() if k != "capa" and v is not None}
        campos["genero"] = id_por_nome("generos", livro["genero"], generos)
        campos["editora"] = id_por_nome("editoras", livro["editora"], editoras)
        capa = PASTA / livro["capa"] if livro.get("capa") else None

        status, dados = requisicao("POST", "/livros/", *multipart(campos, capa))
        if status == 201:
            print(f"+ criado: {livro['titulo']} (id {dados['id']})")
            criados += 1
        else:
            print(f"! erro em {livro['titulo']} ({status}): {dados}")
            erros += 1

    print(f"\n{criados} criados, {ignorados} já existiam, {erros} com erro.")


if __name__ == "__main__":
    main()
