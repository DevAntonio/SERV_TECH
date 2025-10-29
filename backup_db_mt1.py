import sqlite3

#Conecta ao banco original
origem = sqlite3.connect("app/database/servtech.db")


#Cria o arquivo de backup
backup = sqlite3.connect("app/backup/backup_servtech_interno.db")

#Copia o conteúdo com o méttodo interno (sqlite3)
origem.backup(backup)


#Fecha as conexões
backup.close()
origem.close()
print("Backup interno concluído!")