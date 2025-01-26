from flask import Flask, render_template, jsonify, request
import json
import os
from numpy import arange  # Importa a função arange do numpy

app = Flask(__name__)

# Caminho relativo ao diretório onde o script está localizado
script_dir = os.path.dirname(os.path.realpath(__file__))
produtos_path = os.path.join(script_dir, 'produtos.json')

# Carregar o arquivo de produtos
with open(produtos_path, 'r', encoding='utf-8') as f:
    produtos = json.load(f)

# Caminho absoluto da pasta de imagens
pasta_imagens = r"C:\Users\rapha\OneDrive\Área de Trabalho\Sonia_Moda_jeans\static\images"

# Verifica se a pasta de imagens existe
if os.path.exists(pasta_imagens):
    print(f"A pasta foi encontrada: {pasta_imagens}")
    print("Arquivos encontrados na pasta:")
    arquivos_na_pasta = os.listdir(pasta_imagens)
    for arquivo in arquivos_na_pasta:
        print(f"- {arquivo}")
else:
    print(f"A pasta NÃO foi encontrada: {pasta_imagens}")


# Função para calcular a média das avaliações
def calcular_media_avaliacoes(avaliacoes):
    if not avaliacoes:
        return 0  # Se não houver avaliações, retorna 0
    
    try:
        # Convertendo a string de avaliações separadas por vírgulas em uma lista de floats
        avaliacoes_float = [float(avaliacao) for avaliacao in avaliacoes.split(', ')]  
    except ValueError:
        return 0  # Caso algum valor não seja convertido corretamente, retorna 0

    # Calcula a média das avaliações
    resultado = sum(avaliacoes_float) / len(avaliacoes_float)

    # Arredonda para o valor mais próximo entre 0.5 e 5
    if resultado < 0.5:
        return 0.5
    elif resultado <= 1:
        return 1.0
    elif resultado <= 1.5:
        return 1.5
    elif resultado <= 2:
        return 2.0
    elif resultado <= 2.5:
        return 2.5
    elif resultado <= 3:
        return 3.0
    elif resultado <= 3.5:
        return 3.5
    elif resultado <= 4:
        return 4.0
    elif resultado <= 4.5:
        return 4.5
    else:
        return 5.0



# Função para gerar a lista de estrelas
def gerar_estrelas(media_avaliacoes):
    return list(arange(5, 0, -1))  # Passa arange como lista ao invés de float

# Rota para retornar todos os produtos
@app.route('/')
def index():
    return render_template('index.html', produtos=produtos)

# Rota para exibir detalhes do produto
@app.route('/produto/<int:produto_id>')
def exibir_produto(produto_id):
    # Busca o produto pelo ID
    produto = next((p for p in produtos if p['id'] == produto_id), None)
    if produto:
        # Calcula a média das avaliações para exibir no produto
        media_avaliacoes = calcular_media_avaliacoes(produto['avaliacoes'])
        # Gera os valores para as estrelas (de 5 até 0 com intervalos de 0.5)
        estrelas = gerar_estrelas(media_avaliacoes)
        return render_template('produto.html', produto=produto, media_avaliacoes=media_avaliacoes, estrelas=estrelas, arange=arange)
    else:
        return "Produto não encontrado", 404

# Rota para realizar a compra
@app.route('/comprar/<int:produto_id>', methods=['POST'])
def comprar(produto_id):
    for produto in produtos:
        if produto['id'] == produto_id:
            if produto['quantity'] > 0:
                produto['quantity'] -= 1
                return jsonify({"success": True, "message": "Compra realizada com sucesso!"})
            else:
                return jsonify({"success": False, "message": "Produto esgotado!"})
    return jsonify({"success": False, "message": "Produto não encontrado!"})

# Rota para realizar a pesquisa de produtos
@app.route('/pesquisar', methods=['GET'])
def pesquisar_produto():
    # Recebe o termo de pesquisa do frontend
    termo = request.args.get('termo', '')  # Recupera o parâmetro 'termo' da URL

    # Se o termo não estiver vazio, faz a busca
    if termo:
        termo_palavras = termo.lower().split()
        produtos_filtrados = [produto for produto in produtos if all(palavra in produto['name'].lower() for palavra in termo_palavras)]
    else:
        produtos_filtrados = produtos  # Retorna todos os produtos se não houver termo

    # Retorna os produtos filtrados como resposta JSON
    return jsonify(produtos_filtrados)

# Rota para avaliar o produto
@app.route('/avaliar/<int:produto_id>', methods=['POST'])


def avaliar(produto_id):
    # Recupera a avaliação enviada pelo cliente
    avaliacao = request.json.get('avaliacao')
    if avaliacao is None:
        return jsonify({"success": False, "message": "Avaliação não fornecida!"}), 400
    
    # Verifica se a avaliação é válida (de 0.5 a 5)
    if avaliacao not in [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]:
        return jsonify({"success": False, "message": "Avaliação inválida!"}), 400
    
    # Encontra o produto correspondente
    produto = next((p for p in produtos if p['id'] == produto_id), None)
    if produto:
        produto['avaliacoes'].append(avaliacao)  # Adiciona a avaliação à lista de avaliações
        
        # Calcula a nova média
        nova_media = calcular_media_avaliacoes(produto['avaliacoes'])
        
        # Atualiza a média do produto
        produto['media_avaliacoes'] = nova_media
        
        # Converte as avaliações para string, separando por vírgulas
        produto['avaliacoes'] = ', '.join(map(str, produto['avaliacoes']))
        
        # Salva as alterações no arquivo produtos.json com indentação
        with open(produtos_path, 'w', encoding='utf-8') as f:
            json.dump(produtos, f, ensure_ascii=False, indent=4)
        
        return jsonify({"success": True, "message": "Avaliação registrada com sucesso!", "newAverage": nova_media})
    else:
        return jsonify({"success": False, "message": "Produto não encontrado!"}), 404







if __name__ == '__main__':
    app.run(debug=True)
