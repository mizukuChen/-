import struct

# 原始C代码：short length = -5678;
# 使用struct.pack将short整数（有符号2字节）打包为二进制数据，使用本地字节序（'@'）
packed_data = struct.pack('@h', -5678)

# 原始C代码：char send_buf[100]; memcpy(send_buf, p, sizeof(short));
# 创建一个100字节的缓冲区，并将打包后的数据复制到开头
send_buf = bytearray(100)
send_buf[0:len(packed_data)] = packed_data

# 原始C代码：short receive = *(short*)send_buf;
# 从缓冲区前2字节解包出short整数（有符号2字节），使用本地字节序
receive = struct.unpack('@h', send_buf[0:2])[0]

# 原始C代码：printf("%d",receive);
print(receive)