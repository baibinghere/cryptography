# OpenSSL基本用法

## 基本信息

* 查看OpenSSL版本

```bash
openssl version -a
```

* 生成随机N位素数

```bash
openssl prime -generate -bits 64
```

* 快速验证提供的数字是否为素数

*OpenSSL使用一些[算法](https//security.stackexchange.com/questions/176394/how-does-openssl-generate-a-big-prime-number-so-fast)来快速确定某个数字是素数*

```bash
openssl prime 4877
```

## 密匙相关

* 生成一个私钥(Private Key) [最低256位]

```bash
openssl genpkey -algorithm RSA -out key.pem -pkeyopt rsa_keygen_bits:256
```

* 生成一个私钥(Private Key) [任意位数]

```bash
openssl genrsa -out key.pem 32
```

* 读取一个私钥的信息(p, q, n, e, d)

```bash
openssl rsa -in key.pem -text
```

* 根据私钥生成对应的公钥

```bash
openssl rsa -in key.pem -pubout -out pub-key.pem
```

* 读取一个公钥的信息(n, e)

```bash
openssl rsa -in pub-key.pem -pubin -text
```

* 用公钥对文件加密(注意密文长度限制，此例中data.txt内容为1988)

```bash
openssl pkeyutl -encrypt -in data.txt -pubin -inkey pub-key.pem -out encrypt
```

* 用私钥对文件解密

```bash
openssl pkeyutl -decrypt -in encrypt -inkey key.pem -out decypt.txt
```

* textbook RSA

textbook RSA是指使用传统的RSA算法，对数据进行加密解密。这里做了如下测试：

```bash
# 生成128位私钥
openssl genrsa -out key.pem 128
# 生成对应公钥
openssl rsa -in key.pem -pubout -out pub-key.pem
# 准备被加密的数据，在nopad的情况下，数据长度必须与私钥位数一致，例如128位私私钥则需要128位的数据
echo 1234567887654321 > data.txt
# 使用no padding模式对数据进行加密 
openssl pkeyutl -encrypt -in data.txt -pubin -inkey pub-key.pem -out encrypt -pkeyopt rsa_padding_mode:none

#--验证部分--#
# 查看公钥中m,e(0xc368fe392ec77cadb945d18dd4b6e0b1, 0x10001)，加密后的结果
# 0x31323334353637383837363534333231^65537 % 0xc368fe392ec77cadb945d18dd4b6e0b1 = 0x399fece631f18c964fa5fed2031b1bb7
openssl rsa -in pub-key.pem -pubin -text;
# 用Visual Studio Code中的hexdump查看encrypt
# 39 9F EC E6 31 F1 8C 96 4F A5 FE D2 03 1B 1B B7
# 从而证明数据一致
```

## 证书相关

### [标准流程](https://jamielinux.com/docs/openssl-certificate-authority/introduction.html)：

1. 生成ROOT PAIR
1. 生成INTERMEDIATE PAIR
1. 使用INTERMEDIATE KEY签名证书

### 生成ROOT PAIR

```bash
# 选择一个目录，例如/root/ca
mkdir -p /root/ca
cd /root/ca
# 拷贝项目文件中的openssl_rootpair.cnf到/root/ca
cp ~/cryptography/openssl_rootpair.cnf /root/ca/openssl.cnf
# 创建openssl.cnf中定义的对应目录
mkdir certs crl newcerts private
chmod 700 private
touch index.txt
echo 1000 > serial
# 创建root key，需要创建密码
openssl genrsa -aes256 -out private/ca.key.pem 4096
chmod 400 private/ca.key.pem
# 根据root key生成根证书，需要输入根证书密码
openssl req -config openssl.cnf -key private/ca.key.pem -new -x509 -days 7300 -sha256 -extensions v3_ca -out certs/ca.cert.pem
# 确认根证书信息
openssl x509 -noout -text -in certs/ca.cert.pem
```

### 生成INTERMEDIATE PAIR

```bash
# 创建intermediate目录
mkdir /root/ca/intermediate
cd /root/ca/intermediate
# 拷贝项目文件中的openssl_intermediatepair.cnf到/root/ca/intermediate
cp ~/cryptography/openssl_intermediatepair.cnf /root/ca/intermediate/openssl.cnf
mkdir certs crl csr newcerts private
chmod 700 private
touch index.txt
echo 1000 > serial
echo 1000 > crlnumber
# 创建intermediate key，需要创建密码
openssl genrsa -aes256 -out private/intermediate.key.pem 4096
chmod 400 private/intermediate.key.pem
# 根据intermediate key生成CSR(certificate signing request)，需要输入intermediate key的密码
openssl req -config openssl.cnf -new -sha256 -key private/intermediate.key.pem -out csr/intermediate.csr.pem
cd ..
# 根据CSR生成证书，期间需要root key的密码
openssl ca -config openssl.cnf -extensions v3_intermediate_ca -days 3650 -notext -md sha256 -in intermediate/csr/intermediate.csr.pem -out intermediate/certs/intermediate.cert.pem
chmod 444 intermediate/certs/intermediate.cert.pem
# 验证intermediate证书本身
openssl x509 -noout -text -in intermediate/certs/intermediate.cert.pem
# 验证intermediate证书与root证书的关系
openssl verify -CAfile certs/ca.cert.pem intermediate/certs/intermediate.cert.pem
# 创建证书链
cat intermediate/certs/intermediate.cert.pem certs/ca.cert.pem > intermediate/certs/ca-chain.cert.pem
chmod 444 intermediate/certs/ca-chain.cert.pem
```

### 生成SERVER证书

```bash
cd /root/ca
openssl genrsa -aes256 -out intermediate/private/www.cryptoexamples.com.key.pem 2048
chmod 400 intermediate/private/www.cryptoexamples.com.key.pem
cd intermediate
# 生成CSR
openssl req -config openssl.cnf -key private/www.cryptoexamples.com.key.pem -new -sha256 -out csr/www.cryptoexamples.com.csr.pem
# 使用intermediate key对CSR签名
openssl ca -config openssl.cnf -extensions server_cert -days 375 -notext -md sha256 -in csr/www.cryptoexamples.com.csr.pem -out certs/www.cryptoexamples.com.cert.pem
# 验证证书
openssl x509 -noout -text -in certs/www.cryptoexamples.com.cert.pem
# 验证证书链对于该证书的识别
openssl verify -CAfile certs/ca-chain.cert.pem certs/www.cryptoexamples.com.cert.pem
```

### 浏览器验证

要验证浏览器在安装我们生成的根证书后能否正常工作，可用如下方法测试：

1. 将生成的ca-chain.cert.pem转化为der文件，从而可被操作系统识别并安装
```bash
cd /root/ca
# 根证书
openssl x509 -in certs/ca.cert.pem -outform DER -out root_cacert.der
# 中间证书         
openssl x509 -in intermediate/certs/intermediate.cert.pem -outform DER -out intermediate_cacert.der
```
1. 使用项目文件中的server.py启动服务（确保requirements.txt中的包已安装）
```bash
cd /root/ca
# 将www.cryptoexamples.com.key.pem和www.cryptoexamples.com.cert.pem拷贝到server.py目录中
cp intermediate/private/www.cryptoexamples.com.key.pem ~/cryptography
cp intermediate/certs/www.cryptoexamples.com.cert.pem ~/cryptography
# 进入项目目录并运行server.py
cd ~/cryptography
python2 server.py
```

1. 修改DNS使得服务器IP与域名对应

* 在Windows中，修改c:\windows\system32\drivers\etc\hosts
* 在Linux中，修改/etc/hosts

1. 在浏览器中顺利访问：

https://www.cryptoexamples.com

![地址栏](https://github.com/baibinghere/cryptography/blob/master/readme_pictures/FirstLook.PNG)
![证书首页](https://github.com/baibinghere/cryptography/blob/master/readme_pictures/Certificate_General.PNG)
![证书链](https://github.com/baibinghere/cryptography/blob/master/readme_pictures/Certificate_Path.PNG)


## 其它
* 一条命令生成自签名证书

```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365
```

