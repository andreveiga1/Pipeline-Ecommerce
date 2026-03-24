"""
============================================
EXEMPLO 2: Salvar Dados no Banco de Dados PostgreSQL
============================================
Conceito: Salvar dados processados no PostgreSQL usando pandas
Pergunta: Como salvar dados processados em um banco PostgreSQL?

NESTE EXEMPLO VOCÊ APRENDE:
- Como conectar com PostgreSQL usando pandas
- Como salvar DataFrame em tabela SQL
- Por que pandas serve para ler, processar E salvar dados
"""

import io
import boto3
import pandas as pd
from sqlalchemy import create_engine

# Instalar: pip install sqlalchemy psycopg2-binary boto3 pyarrow

# ============================================
# PASSO 1: Ler vendas.parquet do DataLake
# ============================================

SUPABASE_URL = "https://xxxx.supabase.co/storage/v1/s3"
SUPABASE_KEY = "xxxx"
BUCKET_NAME = "datalake"

s3 = boto3.client(
    "s3",
    endpoint_url=SUPABASE_URL,
    aws_access_key_id=SUPABASE_KEY,
    aws_secret_access_key=SUPABASE_KEY,
    region_name="sa-east-1",
)

FILE_KEY = "vendas.parquet"
response = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
parquet_bytes = response["Body"].read()
parquet = io.BytesIO(parquet_bytes)

# Converter Parquet para DataFrame
df_vendas = pd.read_parquet(parquet)

# ============================================
# PASSO 2: Salvar no PostgreSQL
# ============================================

# Configurações do PostgreSQL (Supabase)
# Usar postgresql+psycopg2:// ao invés de postgresql://
DATABASE_URL = "postgresql+psycopg2://xxxx"

# Criar engine de conexão
engine = create_engine(DATABASE_URL)

# Salvar DataFrame em tabela PostgreSQL
# if_exists: 'replace' (substitui), 'append' (adiciona), 'fail' (erro se existir)
df_vendas.to_sql(
    "vendas",  # Nome da tabela
    engine,  # Engine de conexão
    if_exists="replace",  # Substituir se existir
    index=False  # Não salvar índice
)

# Ler dados salvos para verificar
df_verificacao = pd.read_sql_query("SELECT * FROM vendas", engine)

# ============================================
# OUTRAS OPERAÇÕES COM PANDAS E SQL
# ============================================

# Executar query e trazer para pandas
query = """
SELECT
    COUNT(*) as total_vendas,
    SUM(quantidade) as total_quantidade
FROM vendas
"""
df_agregado = pd.read_sql_query(query, engine)

# Fechar conexão
engine.dispose()
