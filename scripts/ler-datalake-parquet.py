"""
============================================
EXEMPLO 1: Conectar com DataLake e Ler Parquet
============================================
Conceito: Conectar com DataLake usando boto3 e ler arquivos Parquet
Pergunta: Como ler dados de um DataLake usando a API S3?
"""

# Instalar boto3: pip install boto3
import boto3

# Configurações do DataLake
S3_ENDPOINT_URL = "https://XXXX.storage.supabase.co/storage/v1/s3"
AWS_REGION = "us-west-2"
AWS_ACCESS_KEY_ID = "XXXX"
AWS_SECRET_ACCESS_KEY = "XXXXX"
BUCKET_NAME = "XXXX"

# Criar cliente S3
s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    endpoint_url=S3_ENDPOINT_URL,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

# Listar arquivos no bucket
response = s3.list_objects(Bucket=BUCKET_NAME)
arquivos = [obj["Key"] for obj in response["Contents"]]

# Instalar pandas: pip install pandas pyarrow
import pandas as pd
# Trabalha com dados "em memória" transforma um bytes
import io

# Baixar arquivo Parquet
FILE_KEY = "vendas.parquet"
response = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
parquet_bytes = response["Body"].read()

# Converter Parquet para DataFrame
df_vendas = pd.read_parquet(io.BytesIO(parquet_bytes))

# ============================================
# EXPLORANDO DADOS COM PANDAS
# ============================================

# Visualizar primeiras linhas
df_vendas.head()

# Visualizar últimas linhas
df_vendas.tail()

# Informações do DataFrame (tipos, memória, etc)
df_vendas.info()

# Estatísticas descritivas (média, mediana, desvio padrão, etc)
df_vendas.describe()

# Estatísticas de uma coluna específica
df_vendas["preco_unitario"].describe()

# Contar valores únicos
df_vendas["id_produto"].value_counts()

# Contar valores únicos com percentual
df_vendas["id_produto"].value_counts(normalize=True)

# Agrupar e agregar dados
# Exemplo: Preço médio por produto
df_vendas.groupby("id_produto")["preco_unitario"].mean()

# Múltiplas agregações
df_vendas.groupby("id_produto")["preco_unitario"].agg(["mean", "min", "max", "count"])

# Agrupar por múltiplas colunas
df_vendas.groupby(["id_produto", "id_cliente"])["quantidade"].sum()

# Filtrar dados
# Vendas com preço maior que 100
df_vendas[df_vendas["preco_unitario"] > 100]

# Filtrar por múltiplas condições
df_vendas[(df_vendas["preco_unitario"] > 100) & (df_vendas["quantidade"] > 1)]

# Ordenar dados
df_vendas.sort_values("preco_unitario", ascending=False)

# Ordenar por múltiplas colunas
df_vendas.sort_values(["id_produto", "preco_unitario"], ascending=[True, False])

# Selecionar colunas específicas
df_vendas[["id_produto", "quantidade", "preco_unitario"]]

# Criar nova coluna calculada
df_vendas["receita"] = df_vendas["quantidade"] * df_vendas["preco_unitario"]

# Contar linhas e colunas
len(df_vendas)  # Número de linhas
df_vendas.shape  # (linhas, colunas)

# Verificar valores únicos
df_vendas["id_produto"].unique()
df_vendas["id_produto"].nunique()  # Quantidade de valores únicos

# Verificar valores faltantes
df_vendas.isnull().sum()

# Verificar duplicatas
df_vendas.duplicated().sum()

# Top N valores
df_vendas.nlargest(10, "preco_unitario")  # Top 10 preços mais altos
df_vendas.nsmallest(10, "preco_unitario")  # Top 10 preços mais baixos

# Converter data_venda para datetime (se necessário)
df_vendas["data_venda"] = pd.to_datetime(df_vendas["data_venda"])

# Agrupar por data e calcular média
df_vendas.groupby(df_vendas["data_venda"].dt.date)["preco_unitario"].mean()
