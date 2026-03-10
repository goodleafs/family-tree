import secrets
import base64

# 生成一个随机的密钥，长度为32字节（256位）
secret_key = base64.urlsafe_b64encode(secrets.token_bytes(32))
print(secret_key.decode())