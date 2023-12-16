import RPi.GPIO as GPIO
import time
#import do Display
import LCD1602
#libs do sensor/camara
import smtplib, ssl
from email.message import EmailMessage
from time import strftime
from picamera import PiCamera
import imghdr
#import do math para criar som personalizado
import math

#inicialização LCD
LCD1602.init(0x27, 1)

#variaveis globais camara/sensor
camera = PiCamera()
data = strftime("%d-%m-%Y-%H%M")
emailSender = 'iot.ismat@gmail.com'
password = 'ynhnqgplzkshpych'
pin_sensor = 4
led_vermelho = 6
#variaveis globais keypad
chave = ''
codigo = ''
tentativas = 0
linhas = 4
col = 4
teclas = ['1','2','3','A',
          '4','5','6','B',
          '7','8','9','C',
          '*','0','#','D'
          ]
pin_linhas = [18,23,24,25]
pin_cols = [10,9,27,17]
#led verde o alarme está desativado
led_verde = 13
#led amarelo o alarme está ativo
led_amarelo = 26
pin_rele = 12
sistema_ligado = True
alarme_ativo = False
pin_buzzer = 16

#Inicializar os Pinos
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(led_verde, GPIO.OUT)
GPIO.setup(led_amarelo, GPIO.OUT)
GPIO.setup(led_vermelho, GPIO.OUT)
GPIO.setup(pin_sensor, GPIO.IN)
GPIO.setup(pin_buzzer, GPIO.OUT)
GPIO.setup(pin_rele, GPIO.OUT)

for pin in pin_linhas:
    GPIO.setup(pin, GPIO.OUT)
    
for pin in pin_cols:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#metodos sensor/camara
def sendMail(msg, dest, subj, image):
    em = EmailMessage()
    em['From'] = emailSender
    em['To'] = dest
    em['Subject'] = subj
    em.set_content(msg)
 
    with open(image, 'rb') as f:
        file_data = f.read()
        file_type = imghdr.what(f.name)
        #print(file_type)
        file_name = f.name

    em.add_attachment(file_data, maintype='image', subtype=file_type, filename=file_name)
    
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(emailSender, password)
        smtp.sendmail(emailSender, dest, em.as_string())

#metodos Keypad
def ler_linha(linha, caracteres):
    global chave
    global codigo
    submit = False
    GPIO.output(linha, GPIO.HIGH)
    if(GPIO.input(pin_cols[0]) == 1):
        #print(caracteres[0])
        chave += caracteres[0]
    if(GPIO.input(pin_cols[1]) == 1):
        #print(caracteres[1])
        chave += caracteres[1]
    if(GPIO.input(pin_cols[2]) == 1):
        #print(caracteres[2])
        chave += caracteres[2]
    if(GPIO.input(pin_cols[3]) == 1):
        if(linha == pin_linhas[3]):
            print('Delete')
            chave = ''
        #print(caracteres[3])
        elif (linha == pin_linhas[2]):
            #tecla "C" verifica se o código inserido é igual à password/chave
            print('Confirmar Código')
            submit = True
            codigo = chave
        else:
            chave += caracteres[3]
        
    GPIO.output(linha, GPIO.LOW)
    
    global tentativas
    global sistema_ligado
    global alarme_ativo
    if (codigo == '1234'):
        if(sistema_ligado):
            print('led_verde ligado - Alarme Desligado')
            alarme_ativo = False
            
        else:
            print('led_amarelo ligado - Alarme Ligado')
   
        time.sleep(0.8)
        sistema_ligado = not sistema_ligado
        codigo = ''
        chave = ''
    else:
        if(submit):
            if(sistema_ligado):
                tentativas += 1
                codigo = ''
                chave = ''
                print('Código errado '+str(3-tentativas)+' tentativas restantes')
                if(tentativas == 3):
                    alarme_ativo = True
                    #GPIO.output(led_vermelho, GPIO.HIGH)
            else:
                codigo = ''
                chave = ''
def ativar_leds():
    global sistema_ligado
    global alarme_ativo
    if(sistema_ligado & (not alarme_ativo)):
        GPIO.output(led_amarelo, GPIO.HIGH)
        GPIO.output(led_vermelho, GPIO.LOW)
        GPIO.output(led_verde, GPIO.LOW)
        GPIO.output(pin_rele, GPIO.HIGH)
        LCD1602.clear()
        LCD1602.write(0,0, 'System ON!')
        LCD1602.write(0,1, 'Cod:' + chave)
        #desligar o buzzer
        p.stop()
        GPIO.output(pin_buzzer, GPIO.LOW)
    elif((not sistema_ligado) & (not alarme_ativo)):
        GPIO.output(led_amarelo, GPIO.LOW)
        GPIO.output(led_vermelho, GPIO.LOW)
        GPIO.output(led_verde, GPIO.HIGH)
        GPIO.output(pin_rele, GPIO.LOW)
        LCD1602.clear()
        LCD1602.write(0,0, 'System OFF!')
        LCD1602.write(0,1, 'Cod:' + chave)
        #desligar o buzzer
        p.stop()
        GPIO.output(pin_buzzer, GPIO.LOW)
    else:
        GPIO.output(led_amarelo, GPIO.LOW)
        GPIO.output(led_vermelho, GPIO.HIGH)
        GPIO.output(led_verde, GPIO.LOW)
        GPIO.output(pin_rele, GPIO.HIGH)
        #ativar o buzzer
        GPIO.output(pin_buzzer, GPIO.HIGH)
        buzz_sound()
        LCD1602.clear()
        LCD1602.write(0,0, '>>INTRUSION<<')
        LCD1602.write(0,1, 'Cod:' + chave)
    time.sleep(0.05)

global p
p = GPIO.PWM(pin_buzzer,1)
p.start(0)
#metodo para criar som
def buzz_sound():
    p.start(50)
    for x in range(0,361):
        sinVal= math.sin(x*(math.pi/180))
        tonVal = 2000 + sinVal * 500
        p.ChangeFrequency(tonVal)
        time.sleep(0.001)

#metodo do LCD Display


if __name__ == '__main__':
    #GPIO.output(led_vermelho, GPIO.LOW)
    print(data)
    ativar_leds()
    #GPIO.output(led_amarelo, GPIO.HIGH)
    print('ativando o sensor')
    time.sleep(2)
    
    try:
        while True:
            #LCD1602.write(0,0, 'Hello world!')
            #LCD1602.write(0,1, 'Welcome!')
            #camara/sensor
            
            ativar_leds()
            if(sistema_ligado):
                if(GPIO.input(pin_sensor) == GPIO.HIGH):
                    print('detetado movimento')
                    camera.start_preview()
                    #GPIO.output(led_vermelho, GPIO.HIGH)
                    alarme_ativo = True
                    msg = '>>ATENÇÃO<<\nFoi detetada uma intrusão!'
                    dest = 'claudiocoelho181@hotmail.com'
                    subj = 'Alarm System message'
                    time.sleep(0.5)
                    #GPIO.output(led_vermelho, GPIO.LOW)
                    camera.capture('/home/pi/Desktop/TP3-Rasp/Intrusions/intruder'+ data +'.jpg')
                    camera.stop_preview()
                    time.sleep(0.5)
                    sendMail(msg, dest, subj, '../Intrusions/intruder'+ data +'.jpg')
                    #camera.close()
            
            #Keypad
            ler_linha(pin_linhas[0], ["1","2","3","A"])
            ler_linha(pin_linhas[1], ["4","5","6","B"])
            ler_linha(pin_linhas[2], ["7","8","9","C"])
            ler_linha(pin_linhas[3], ["*","0","#","D"])
            time.sleep(0.2)
            print(chave)
        
    except KeyboardInterrupt:
        print('Programa encerrado!')
        GPIO.output(led_verde, GPIO.LOW)
        GPIO.output(led_vermelho, GPIO.LOW)
        GPIO.output(led_amarelo, GPIO.LOW)
        GPIO.output(pin_buzzer, GPIO.LOW)
        GPIO.output(pin_rele, GPIO.LOW)
        LCD1602.clear()
        GPIO.cleanup()
        print('LCD Good to True')
        
        
        
########## TODO #######
# 1. Fazer ativação/desativação do sistema de segurança - FEITO
# 2. Fazer com que o sensor desative temporariamente apos uma intrusao (5 segundos) 
# 3. Ao introduzir o codigo errado 3 vezes e ao detetar uma intrusão, dispara o alarme - FEITO
# 4. Adicionar o LCD - SYSTEM ON/OFF | Cod: | INTRUSION
# 5. Adicionar o buzer
#
