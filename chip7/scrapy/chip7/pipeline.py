import mysql.connector
from chip7.settings import (
    DB_HOST, DB_USER, DB_PASSWORD, DB_NAME,
    DB_TABLE_CATEGORIAS, DB_TABLE_PRODUTOS,
    COL_CAT_ID_CATEGORIA, COL_CAT_NOME,
    COL_PROD_TITULO, COL_PROD_DESCRICAO, COL_PROD_PRECO,
    COL_PROD_DISPONIBILIDADE, COL_PROD_ID_CATEGORIA, COL_PROD_CODIGO
)

class Chip7toPipeline:
    def __init__(self):
        # inicializa a None para o close_spider não dar AttributeError
        self.conn   = None
        self.cursor = None

    def open_spider(self, spider):
        # liga à base de dados
        try:
            self.conn   = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            self.cursor = self.conn.cursor()    # o cursor é o objeto que executa as queries na base de dados
        except mysql.connector.Error as e:
            spider.logger.error(f"Erro ao ligar à base de dados: {e}")
            raise  #PARA e dá o erro

        # cria a categoria se não existir, ignora se já existir
        try:
            self.cursor.execute(f"""
                INSERT IGNORE INTO {DB_TABLE_CATEGORIAS} ({COL_CAT_NOME}) VALUES (%s)
            """, (spider.name,))                # COL_CAT_NOME precisa ser UNIQUE
            self.conn.commit()                  # confirma e grava as alterações na base de dados
        except mysql.connector.Error as e:
            spider.logger.error(f"Erro ao criar categoria '{spider.name}': {e}")
            raise

        # busca o id da categoria
        try:
            self.cursor.execute(f"""
                SELECT {COL_CAT_ID_CATEGORIA} FROM {DB_TABLE_CATEGORIAS} WHERE {COL_CAT_NOME} = %s
            """, (spider.name,))
            self.id_categoria = self.cursor.fetchone()[0]  # seleciona o id do array dos resultados que dá
        except mysql.connector.Error as e:
            spider.logger.error(f"Erro ao buscar id da categoria '{spider.name}': {e}")
            raise




    def process_item(self, item):
        # PARA GUARDAR NA BD
        try:
            item["preco"] = self._limpar_preco(item["preco"])
        except ValueError as e:
            # preço não foi bem convertido
            raise ValueError(f"Preço inválido '{item.get('preco')}': {e}")

        try:
            self.cursor.execute(f"""
            INSERT IGNORE INTO {DB_TABLE_PRODUTOS}
                ({COL_PROD_TITULO}, {COL_PROD_DESCRICAO}, {COL_PROD_PRECO}, {COL_PROD_DISPONIBILIDADE}, {COL_PROD_ID_CATEGORIA}, {COL_PROD_CODIGO})
            VALUES (%s, %s, %s, %s, %s, %s) """, (item["titulo"], item["descricao"], item["preco"], item["disponibilidade"], self.id_categoria, item["codigo"]))
            self.conn.commit()                  # confirma e grava as alterações na base de dados
        except mysql.connector.Error as e:
            self.conn.rollback()                # desfaz o insert se algo correr mal
            raise

        return item

    @staticmethod
    def _limpar_preco(preco_raw):
        # remove €, espaços e converte vírgula em ponto para DECIMAL
        preco = preco_raw.replace("€", "").replace(" ", "").replace(",", ".")
        return float(preco)

    #quando acaba
    def close_spider(self):
        # fecha o cursor e a ligação à base de dados
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()