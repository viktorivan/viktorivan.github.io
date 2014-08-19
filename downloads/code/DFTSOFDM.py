#Programa DFTS-OFDM

#Para ejecutar se requiere de scipy y matplotlib
#Desde una terminal ejecute: 
# sudo apt-get install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose python-tk
#La simulacion la puede correr desde una terminal
# python DFTSOFDM.py

#Carga de bibliotecas
import scipy
import numpy
import matplotlib.pyplot

numpy.set_printoptions(precision=4,suppress=True)

#Datos de inicializacion
print "Inicializando parametros de simulacion"
snr = numpy.arange(0,33,8)
taps = 1.
itera = 1000.
paq = numpy.shape(snr)[0]*itera
datasize = 768
gx = "04C11DB7"
polsize = 32
dfts = 192
ofdm = 2048
cp = ofdm/4
pilot = 4
pilot_carriers = [-61,-31,31,61]
dfts_carriers = [x for x in (range(-((dfts+pilot)/2),0,1) + range(1,(dfts+pilot)/2+1,1)) if x not in pilot_carriers]

### TRANSMISOR ###

#Generacion de datos aleatorios
print "Generando bits de datos aleatorios"
datab = numpy.random.randint(2, size=(datasize-polsize)*paq)
datab = numpy.reshape(datab,(paq,-1))

#Etapa CRC
print "Calculando CRC"
pol = numpy.array([int(y) for x in bin(int(str(gx), 16))[2:].zfill(polsize).rjust(polsize+1,'1') for y in x])
datazeros = numpy.concatenate((datab,numpy.zeros((paq,polsize),dtype=numpy.int)),1)
datacrc = datazeros.copy()

#Calculo CRC
for j in range(scipy.shape(datazeros)[0]):
	for i in range(scipy.shape(datazeros)[1]): 
		if datazeros[j,i]==1 and i+scipy.shape(pol)[0]-1 < scipy.shape(datazeros)[1]: 
			datazeros[j,i:scipy.shape(pol)[0]+i] = datazeros[j,i:scipy.shape(pol)[0]+i]^pol

#Datos con CRC
datacrc = datacrc|datazeros

#Modulador 16-QAM
print "Datos en el modulador digital"
dataqam = numpy.reshape(datacrc,(-1,4))
dataqam [:,[0,1]] = dataqam [:,[0,1]]*2-1
dataqam [:,[2,3]] = -(dataqam [:,[2,3]]*2-3)
datam = dataqam[:,0]*dataqam[:,2] + dataqam[:,1]*dataqam[:,3]*1j

#DFTS
print "Aplicando DFTS"
datadfts = numpy.reshape(datam,(-1,dfts))

for i in range(scipy.shape(datadfts)[0]):
	datadfts[i,0:scipy.shape(datadfts)[1]] = numpy.fft.fft(datadfts[i,0:scipy.shape(datadfts)[1]])

#OFDM
print "En el transmisor OFDM"
#Generacion de ceros y pilotos
datapilot = numpy.reshape(numpy.random.randint(2,size=paq*pilot)*2-1,(paq,-1))
dataofdm = numpy.zeros((paq,ofdm),dtype=numpy.complex)

#Asignacion de portadoras
dataofdm[:,pilot_carriers] = datapilot
dataofdm[:,dfts_carriers] = datadfts

#IFFT
for i in range(scipy.shape(dataofdm)[0]):
	dataofdm[i,0:scipy.shape(dataofdm)[1]] = numpy.fft.ifft(dataofdm[i,0:scipy.shape(dataofdm)[1]])

#Prefijo ciclico
dataofdm = numpy.concatenate((dataofdm[:,ofdm-cp:ofdm],dataofdm),1)

### CANAL ###
#Multitrayectoria
print "Agregando multitrayectorias del canal"
h = 1/numpy.sqrt(2*taps)*(numpy.random.randn(scipy.shape(dataofdm)[0],taps) + numpy.random.randn(scipy.shape(dataofdm)[0],taps)*1j)
h = numpy.reshape((numpy.tile(1./(numpy.arange(taps)+1),scipy.shape(dataofdm)[0])),(-1,taps))*h
H = numpy.zeros((paq,ofdm+cp),dtype=numpy.complex)
datacanal = numpy.zeros((paq,ofdm+cp),dtype=numpy.complex)

for i in range(scipy.shape(dataofdm)[0]):
	H[i] = numpy.fft.fft(h[i]/numpy.linalg.norm(h[i]),ofdm+cp)
	datacanal[i] = numpy.fft.fft(dataofdm[i])

datacanal = datacanal*H;

for i in range(scipy.shape(dataofdm)[0]):
	datacanal[i] = numpy.fft.ifft(datacanal[i])    
  
#AWGN
print "Sumando AWGN a los datos"
ebno = numpy.sqrt(numpy.reshape(numpy.repeat(10**(snr/10.),scipy.shape(datacanal)[1]*scipy.shape(datacanal)[0]/scipy.shape(snr)[0]),(-1,scipy.shape(datacanal)[1])))
awgn = (numpy.random.randn(scipy.shape(datacanal)[0],scipy.shape(datacanal)[1]) + numpy.random.randn(scipy.shape(datacanal)[0],scipy.shape(datacanal)[1])*1j)/(numpy.sqrt(2)*ebno)
datacanal = datacanal + awgn

### RECEPTOR ###
print "En el receptor OFDM"
#Remueve el prefijo ciclico
dataiofdm = datacanal[:,cp:ofdm+cp].copy()

#FFT
for i in range(scipy.shape(dataiofdm)[0]):
	dataiofdm[i,0:scipy.shape(dataiofdm)[1]] = numpy.fft.fft(dataiofdm[i,0:scipy.shape(dataiofdm)[1]])

#Ecualizador
print "Ecualizando los datos recibidos"
dataiofdm = dataiofdm[:,dfts_carriers].copy()/H[:,dfts_carriers]

#IDFTS
print "Calculando IDFTS"
for i in range(scipy.shape(dataiofdm)[0]):
	dataiofdm[i,0:scipy.shape(dataiofdm)[1]] = numpy.fft.ifft(dataiofdm[i,0:scipy.shape(dataiofdm)[1]])

#Demodulador 16-QAM
print "Demodulador digital"
datadem = numpy.reshape(dataiofdm,(1,-1))
datadem = numpy.transpose(numpy.vstack((numpy.real(datadem)>0,numpy.imag(datadem)>0,numpy.absolute(numpy.real(datadem))<2,numpy.absolute(numpy.imag(datadem))<2))*1)

#Recepcion para calculo de CRC
print "Calculo de CRC Check"
datarcrc = numpy.reshape(datadem,(paq,-1))
datarx = datarcrc.copy()

#Calculo de CRC
for j in range(scipy.shape(datarcrc)[0]):
	for i in range(scipy.shape(datarcrc)[1]):
		if datarcrc[j,i]==1 and i+scipy.shape(pol)[0]-1 < scipy.shape(datarcrc)[1]:
			datarcrc[j,i:scipy.shape(pol)[0]+i] = datarcrc[j,i:scipy.shape(pol)[0]+i]^pol

#Eliminacion del CRC y paquetes incorrectos
datar = datarx[:,0:datasize-polsize].copy()

#Contador de paquetes correctos de acuerdo al CRC
print "Calculando PER"
per = numpy.sum(numpy.reshape(((numpy.sum(datarcrc,1)!=0)*1),(-1,itera)),1)/itera

#Comparacion entre datab y datar y promedia errores de acuerdo a iteraciones
print "Calculando BER"
ber = numpy.sum((numpy.reshape(numpy.sum(numpy.absolute(datar-datab), axis=1),(-1,itera))),1)/(itera*(datasize-polsize))

print "SNR %BER %PER"
print numpy.vstack([snr,ber*100,per*100]).T
matplotlib.pyplot.semilogy(snr,per,snr,ber)
matplotlib.pyplot.legend(["PER","BER"])
matplotlib.pyplot.show()
