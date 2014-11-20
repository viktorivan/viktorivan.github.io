#Programa DFTS-OFDM

#Para ejecutar se requiere de scipy y matplotlib
#Desde una terminal ejecute: 
# sudo apt-get install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose python-tk
#La simulacion la puede correr desde una terminal
# python DFTSOFDMSNR.py

#Carga de bibliotecas
import scipy as sp
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.set_printoptions(precision=4,suppress=True,threshold='nan')

#Datos de inicializacion
#print "Inicializando parametros de simulacion"
ebno = np.arange(0,15,1)
taps = 1.
paqsnr = 1000.
paq = np.shape(ebno)[0]*paqsnr
datasize = 768
gx = "04C11DB7"
polsize = 32
dfts = 192
ofdm = 2048
cp = ofdm/4
pilot = 4
pilot_carriers = [-61,-31,31,61]
dfts_carriers = [x for x in (range(-((dfts+pilot)/2),0,1) + range(1,(dfts+pilot)/2+1,1)) if x not in pilot_carriers]
zero_carriers = np.array([x for x in (range (0,1950)) if x not in range(1,99)])

### TRANSMISOR ###

#Generacion de datos aleatorios
#print "Generando bits de datos aleatorios"
datab = np.random.randint(2, size=(datasize-polsize)*paq)
datab = np.reshape(datab,(paq,-1))

#Etapa CRC
#print "Calculando CRC"
pol = np.array([int(y) for x in bin(int(str(gx), 16))[2:].zfill(polsize).rjust(polsize+1,'1') for y in x])
datazeros = np.concatenate((datab,np.zeros((paq,polsize),dtype=np.int)),1)
datacrc = datazeros.copy()

#Calculo CRC
for j in range(sp.shape(datazeros)[0]):
	for i in range(sp.shape(datazeros)[1]): 
		if datazeros[j,i]==1 and i+sp.shape(pol)[0]-1 < sp.shape(datazeros)[1]: 
			datazeros[j,i:sp.shape(pol)[0]+i] = datazeros[j,i:sp.shape(pol)[0]+i]^pol

#Datos con CRC
datacrc = datacrc|datazeros

#Modulador 16-QAM
#print "Datos en el modulador digital"
dataqam = np.reshape(datacrc,(-1,4))
dataqam [:,[0,1]] = dataqam [:,[0,1]]*2-1
dataqam [:,[2,3]] = -(dataqam [:,[2,3]]*2-3)
datam = (dataqam[:,0]*dataqam[:,2] + dataqam[:,1]*dataqam[:,3]*1j)*np.sqrt(10)

#DFTS
#print "Aplicando DFTS"
datadfts = np.reshape(datam,(-1,dfts))

for i in range(sp.shape(datadfts)[0]):
	datadfts[i,0:sp.shape(datadfts)[1]] = np.fft.fft(datadfts[i,0:sp.shape(datadfts)[1]])
	
#OFDM
#print "En el transmisor OFDM"
#Generacion de ceros y pilotos
datapilot = np.reshape(np.random.randint(2,size=paq*pilot)*2-1,(paq,-1))
dataofdm = np.zeros((paq,ofdm),dtype=np.complex)

#Asignacion de portadoras
dataofdm[:,pilot_carriers] = datapilot
dataofdm[:,dfts_carriers] = datadfts

#IFFT
for i in range(sp.shape(dataofdm)[0]):
	dataofdm[i,0:sp.shape(dataofdm)[1]] = np.fft.ifft(dataofdm[i,0:sp.shape(dataofdm)[1]])

#Prefijo ciclico
dataofdm = np.concatenate((dataofdm[:,ofdm-cp:ofdm],dataofdm),1)

### CANAL ###
#Multitrayectoria
#print "Agregando multitrayectorias del canal"
h = 1/np.sqrt(2*taps)*(np.random.randn(sp.shape(dataofdm)[0],taps) + np.random.randn(sp.shape(dataofdm)[0],taps)*1j)
h = np.reshape((np.tile(1./(np.arange(taps)+1),sp.shape(dataofdm)[0])),(-1,taps))*h
H = np.zeros((paq,ofdm+cp),dtype=np.complex)
datacanal = np.zeros((paq,ofdm+cp),dtype=np.complex)

for i in range(sp.shape(dataofdm)[0]):
	H[i] = np.fft.fft(h[i]/np.linalg.norm(h[i]),ofdm+cp)
	datacanal[i] = np.fft.fft(dataofdm[i])

datacanal = datacanal*H;

for i in range(sp.shape(dataofdm)[0]):
	datacanal[i] = np.fft.ifft(datacanal[i])    
  
#AWGN
#print "Sumando AWGN a los datos"
snr = np.sqrt(np.reshape(np.repeat(10**(ebno/10.),sp.shape(datacanal)[1]*sp.shape(datacanal)[0]/sp.shape(ebno)[0]),(-1,sp.shape(datacanal)[1])))
awgn = (np.random.randn(sp.shape(datacanal)[0],sp.shape(datacanal)[1]) + np.random.randn(sp.shape(datacanal)[0],sp.shape(datacanal)[1])*1j)/(np.sqrt(2)*snr)
datacanal = datacanal + awgn

### RECEPTOR ###
#print "En el receptor OFDM"
#Remueve el prefijo ciclico
dataiofdm = datacanal[:,cp:ofdm+cp].copy()

#FFT
for i in range(sp.shape(dataiofdm)[0]):
	dataiofdm[i,0:sp.shape(dataiofdm)[1]] = np.fft.fft(dataiofdm[i,0:sp.shape(dataiofdm)[1]])

#Calculo de SNR estimado

snrest = 10*np.log10(np.sum(np.sum(np.square(np.absolute(dataiofdm.reshape((-1, paqsnr,ofdm)))),axis=2),axis=1) / np.sum(
np.sum(np.square(np.absolute(dataiofdm[:][:,zero_carriers].reshape((-1, paqsnr,ofdm-dfts-pilot)))),axis=2),axis=1) * ((
np.linalg.norm(ofdm-dfts-pilot)/np.linalg.norm(ofdm)))-1)

#Ecualizador
#print "Ecualizando los datos recibidos"
dataiofdm = dataiofdm[:,dfts_carriers].copy()/H[:,dfts_carriers]

#IDFTS
#print "Calculando IDFTS"
for i in range(sp.shape(dataiofdm)[0]):
	dataiofdm[i,0:sp.shape(dataiofdm)[1]] = np.fft.ifft(dataiofdm[i,0:sp.shape(dataiofdm)[1]])

#Demodulador 16-QAM
#print "Demodulador digital"
datadem = np.reshape(dataiofdm,(1,-1))/np.sqrt(10)
datadem = np.transpose(np.vstack((np.real(datadem)>0,np.imag(datadem)>0,np.absolute(np.real(datadem))<2,np.absolute(np.imag(datadem))<2))*1)

#Recepcion para calculo de CRC
#print "Calculo de CRC Check"
datarcrc = np.reshape(datadem,(paq,-1))
datarx = datarcrc.copy()

#Calculo de CRC
for j in range(sp.shape(datarcrc)[0]):
	for i in range(sp.shape(datarcrc)[1]):
		if datarcrc[j,i]==1 and i+sp.shape(pol)[0]-1 < sp.shape(datarcrc)[1]:
			datarcrc[j,i:sp.shape(pol)[0]+i] = datarcrc[j,i:sp.shape(pol)[0]+i]^pol

#Eliminacion del CRC y paquetes incorrectos
datar = datarx[:,0:datasize-polsize].copy()

#Contador de paquetes correctos de acuerdo al CRC
#print "Calculando PER"
per = np.sum(np.reshape(((np.sum(datarcrc,1)!=0)*1),(-1,paqsnr)),1)/paqsnr

#Comparacion entre datab y datar y promedia errores de acuerdo a iteraciones
#print "Calculando BER"
ber = np.sum((np.reshape(np.sum(np.absolute(datar-datab), axis=1),(-1,paqsnr))),1)/(paqsnr*(datasize-polsize))

print "SNR %BER %PER SNRest"
print np.vstack([ebno,ber*100,per*100,snrest]).T

leg1 = ["BER", "PER"]
leg2 = ["SNR est", "SNR real"]

fig, ax1 = plt.subplots()
plt.title('Bit Error Rate For A DFTS-OFDM System')
ax1.set_color_cycle(['r', 'm'])
ax1.semilogy(ebno,ber,'-*',ebno,per,'-+')
ax1.set_xlabel('SNR')
ax1.legend(leg1, loc=3)
ax2 = ax1.twinx()
ax2.plot(ebno,snrest,'v',ebno,ebno,'--')
ax2.legend(leg2, loc=2)
plt.show()
plt.savefig('dftsofdmsnr.eps')
