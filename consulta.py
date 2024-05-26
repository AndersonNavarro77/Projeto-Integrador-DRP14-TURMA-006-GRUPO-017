from decimal import Decimal
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__, template_folder="templates")

# Função para conectar ao banco de dados
def conectar_banco():
    conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="consultadebito"
    )
    return conexao

# Função para obter todos os clientes
def obter_todos_clientes():
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM clientes')
    clientes = cursor.fetchall()
    conexao.close()
    return clientes

def obter_id_cliente_por_nome(nome_cliente):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute('SELECT id FROM clientes WHERE nome = %s', (nome_cliente,))
    cliente_id = cursor.fetchone()
    conexao.close()
    return cliente_id[0] if cliente_id else None

# Função para verificar se um cliente está em débito e retornar o valor do débito
def verificar_debito(cliente_id):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute('SELECT IFNULL(SUM(valor), 0) FROM debitos WHERE cliente_id = %s', (cliente_id,))
    debito = cursor.fetchone()[0]
    conexao.close()
    return debito

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastrar_cliente', methods=['GET', 'POST'])
def cadastrar_cliente_template():  # Renomeada para cadastrar_cliente_template
    if request.method == 'POST':
        # Lógica para cadastrar o cliente
        return render_template('cadastro.html')

@app.route('/consultar_cliente')
def consultar_cliente_form():
    # Aqui você pode adicionar a lógica para renderizar o formulário de consulta de cliente
    return render_template('consultar_cliente_form.html')

@app.route('/consultar_debito', methods=['GET', 'POST'])
def consultar_debito():
    if request.method == 'POST':
        if 'nome_cliente' in request.form:
            nome_cliente = request.form['nome_cliente']
            cliente_id = obter_id_cliente_por_nome(nome_cliente)
            if cliente_id is not None:
                debito = verificar_debito(cliente_id)
                mensagem = 'Cliente em dia!' if debito == 0 else None
                return render_template('resultado.html', debito=debito, mensagem=mensagem)
            else:
                return render_template('resultado.html', mensagem='Cliente não encontrado.', debito=None)
        else:
            return render_template('resultado.html', mensagem='Nome do cliente não enviado.', debito=None)
    # Se a requisição for GET, renderize o template para visualizar os débitos
    return render_template('consulta_debito_form.html')
 
@app.route('/cadastro_cliente', methods=['GET', 'POST'])
def cadastrar_cliente():
    if request.method == 'POST':
        # Lógica para cadastrar o cliente
        nome_cliente = request.form['nome_cliente']
        telefone = request.form['telefone']
        email = request.form['email']
        conexao = conectar_banco()
        cursor = conexao.cursor()
        cursor.execute('INSERT INTO clientes (nome, telefone, email) VALUES (%s, %s, %s)', (nome_cliente, telefone, email))
        conexao.commit()
        conexao.close()
        mensagem = 'Cliente incluído com sucesso!'
        return render_template('cadastro_cliente.html', mensagem=mensagem)
    return render_template('cadastro_cliente.html')

@app.route('/incluir_debito', methods=['GET', 'POST'])
def incluir_debito():
    if request.method == 'POST':
        nome_cliente = request.form['nome_cliente']
        valor = request.form['valor']
        
        try:
            # Remover pontos e substituir vírgula por ponto no valor
            valor_formatado = valor.replace('.', '').replace(',', '.')
            
            # Converta o valor para Decimal
            valor_decimal = Decimal(valor_formatado)
        except ValueError:
            # Se ocorrer um erro ao converter o valor para Decimal
            return render_template('incluir.html', mensagem='Valor inválido.')

        cliente_id = obter_id_cliente_por_nome(nome_cliente)
        if cliente_id is not None:
            conexao = conectar_banco()
            cursor = conexao.cursor()
            try:
                cursor.execute('INSERT INTO debitos (cliente_id, valor) VALUES (%s, %s)', (cliente_id, valor_decimal))
                conexao.commit()
                conexao.close()
                return redirect(url_for('index'))
            except mysql.connector.Error as err:
                # Se ocorrer um erro ao inserir no banco de dados
                return render_template('incluir.html', mensagem='Erro ao inserir débito no banco de dados.')
        else:
            return render_template('incluir.html', mensagem='Cliente não encontrado.')
    return render_template('incluir.html')

@app.route('/incluir_debito_form')
def incluir_debito_form():
    return render_template('incluir_debito.html')

@app.route('/excluir_debito_form')
def excluir_debito_form():
    return render_template('excluir_form.html')

@app.route('/incluir_debito_processar', methods=['POST'])
def processar_inclusao_debito():
    if request.method == 'POST':
        if 'nome_cliente' in request.form and 'valor' in request.form:
            nome_cliente = request.form['nome_cliente']
            valor = request.form['valor']
            cliente_id = obter_id_cliente_por_nome(nome_cliente)
            if cliente_id is not None:
                conexao = conectar_banco()
                cursor = conexao.cursor()
                cursor.execute('INSERT INTO debitos (cliente_id, valor) VALUES (%s, %s)', (cliente_id, valor))
                conexao.commit()
                conexao.close()
                return redirect(url_for('index'))
            else:
                return render_template('incluir.html', mensagem='Cliente não encontrado.')
        else:
            return render_template('incluir.html', mensagem='Dados incompletos.')
    return render_template('incluir.html')

@app.route('/excluir_debito', methods=['GET', 'POST'])
def excluir_debito():
    if request.method == 'POST':
        nome_cliente = request.form['nome_cliente']
        cliente_id = obter_id_cliente_por_nome(nome_cliente)
        if cliente_id is not None:
            conexao = conectar_banco()
            cursor = conexao.cursor()
            cursor.execute('DELETE FROM debitos WHERE cliente_id = %s', (cliente_id,))
            conexao.commit()
            conexao.close()
            return redirect(url_for('index'))
        else:
            return render_template('excluir.html', mensagem='Cliente não encontrado.')
    return render_template('excluir.html')

@app.route('/selecionar_acao', methods=['POST'])
def selecionar_acao():
    acao = request.form['acao']
    if acao == 'cadastrar_cliente':
        return redirect(url_for('cadastrar_cliente'))
    elif acao == 'cadastrar_debito':
        return redirect(url_for('incluir_debito_form'))  # Alteração aqui
    elif acao == 'visualizar_debito':
        return redirect(url_for('consultar_debito'))
    else:
        return redirect(url_for('index'))

@app.route('/visualizar_debito/<nome_cliente>', methods=['GET'])
def visualizar_debito(nome_cliente):
    cliente_id = obter_id_cliente_por_nome(nome_cliente)
    if cliente_id is not None:
        conexao = conectar_banco()
        cursor = conexao.cursor()
        cursor.execute('SELECT valor FROM debitos WHERE cliente_id = %s', (cliente_id,))
        debitos = cursor.fetchall()
        total_debito = sum(debito[0] for debito in debitos)
        conexao.close()
        return render_template('visualizar_debito.html', nome_cliente=nome_cliente, debitos=debitos, total_debito=total_debito)
    else:
        return render_template('visualizar_debito.html', mensagem='Cliente não encontrado.')

try:
    conexao = conectar_banco()
except mysql.connector.Error as err:
    print("Erro ao conectar ao banco de dados:", err)

if __name__ == '__main__':
    app.run(debug=True)