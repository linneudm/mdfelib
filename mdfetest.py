import requests
import re
from io import StringIO
import sys
from mdfelib.v3_00 import mdfe as mdfe3
from mdfelib.v3_00 import mdfeModalRodoviario as rodo3
from pynfe.processamento.comunicacao import ComunicacaoSefaz
from pynfe.entidades.cliente import Cliente
from pynfe.entidades.emitente import Emitente
from pynfe.entidades.notafiscal import NotaFiscal
from pynfe.entidades.fonte_dados import _fonte_dados
from pynfe.processamento.serializacao import SerializacaoXML, SerializacaoQrcode
from pynfe.processamento.assinatura import AssinaturaA1
from pynfe.entidades.certificado import CertificadoA1
from pynfe.utils.flags import CODIGO_BRASIL
from decimal import Decimal
from pynfe.utils.flags import (
    NAMESPACE_NFE,
    NAMESPACE_XSD,
    NAMESPACE_XSI,
    VERSAO_PADRAO,
    NAMESPACE_SOAP,
    CODIGOS_ESTADOS,
    NAMESPACE_BETHA,
    NAMESPACE_METODO
)
from pynfe.utils import etree, so_numeros
import datetime
from lxml import etree as etree_
#import lxml
import os

ender_emit = mdfe3.TEndeEmi(
    xLgr='Rua',
    nro='150',
    xBairro='Centro',
    cMun='2305506',
    xMun='IGUATU',
    CEP='63500000',
    UF='CE',
    fone='08002755700'
)

emit = mdfe3.emitType(
    CNPJ='15443409000150',
    IE='194995925',
    xNome='Razao Social',
    xFant='Fantasia',
    enderEmit=ender_emit)

carregamento_1 = mdfe3.infMunCarregaType(
    cMunCarrega='2305506',
    xMunCarrega='TESTE'
)
#Formato AAAA-MM-DDTHH:MM:DD TZD
ide = mdfe3.ideType(
    cUF='23',
    tpAmb=2,
    tpEmit=1,
    tpTransp=None,
    mod=58,
    serie='1',
    nMDF='1',
    cMDF='00004894',
    cDV='4',
    modal=1,
    dhEmi='2019-03-26T13:58:06-03:00',
    tpEmis=1,
    procEmi='0',
    verProc='Odoo',
    UFIni='CE',
    UFFim='CE',
    infMunCarrega=[carregamento_1],
    infPercurso=None,
    dhIniViagem=None,
    indCanalVerde=None,
)

tot = mdfe3.totType(
    qCTe=None,
    qNFe='2',
    qMDFe=None,
    vCarga='3044.00',
    cUnid='01',
    qCarga='57.0000',
)

lista_cte = []
lista_nfe = []


nfe_1 = mdfe3.infNFeType(
    chNFe='23180341426966004836558720000002681197872700',
    SegCodBarra=None,
    indReentrega=None,
    infUnidTransp=None,
    peri=None,
)

nfe_2 = mdfe3.infNFeType(
    chNFe='23180341426966003600558720000012321410321707',
    SegCodBarra=None,
    indReentrega=None,
    infUnidTransp=None,
    peri=None,
)

lista_nfe.append(nfe_1)
lista_nfe.append(nfe_2)

infMunDescarga= mdfe3.infMunDescargaType(
    cMunDescarga='2305506',
    xMunDescarga='Cidade',
    infCTe=lista_cte,
    infNFe=lista_nfe,
    infMDFeTransp=None,
)

infDoc= mdfe3.infDocType(infMunDescarga=[infMunDescarga])

condutor_1 = rodo3.condutorType(
    xNome='LuisFelipeMileo',
    CPF='33333333333'
)

veiculo = rodo3.veicTracaoType(
    cInt='0001',
    placa='PMR3000',
    RENAVAM=None,
    tara='4250',
    capKG='0',
    capM3='0',
    prop=None,
    condutor=[condutor_1],
    tpRod='02',
    tpCar='02',
    UF='CE'
)

rodo = rodo3.rodo(
    infANTT=None,
    veicTracao=veiculo,
    veicReboque=None,
    codAgPorto=None,
    lacRodo=None
)

modal = mdfe3.infModalType(versaoModal="3.00", anytypeobjs_=rodo)

mdfe = mdfe3.MountMDFeType(
    versao="3.00", Id="MDFe35140210142785000190580010000000021491283024", ide=ide, emit=emit, infModal=modal,
    infDoc=infDoc, seg=None, tot=tot, lacres=None, autXML=None,
    infAdic=None
)

f = open("file.txt", "w")
xml = mdfe.export(f, 0, pretty_print=False)
f.close()
f = open("file.txt", "r")
xml = f.read()
xml = etree.XML(xml)

xml = mdfe.construir_xml_soap('MDFe', xml)

certificado = os.path.realpath('../../') + '/cert.pfx'
senha = "1234"

url =  mdfe3.urls_webservice(1,2)

def mypost_header():
    """Retorna um dicionário com os atributos para o cabeçalho da requisição HTTP"""
    # PE é a única UF que exige SOAPAction no header
    uf = "RS"
    #####
    response = {
        #'Host': "http://www.portalfiscal.inf.br/mdfe/wsdl/MDFeRetRecepcao",
        'content-type': 'application/soap+xml; charset=utf-8;',
        'Accept': 'application/soap+xml; charset=utf-8;',
        #'SOAPAction': 'http://www.portalfiscal.inf.br/mdfe/wsdl/MDFeRetRecepcao',
    }
    #if uf.upper() == 'PE':
        #response["SOAPAction"] = ""
    return response

def mypost(xml, url, chave_cert):
    print(etree_.tostring(xml))
    try:
        xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>'

        # limpa xml com caracteres bugados para infNFeSupl em NFC-e
        xml = re.sub(
            '<qrCode>(.*?)</qrCode>',
            lambda x: x.group(0).replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', ''),
            etree_.tostring(xml, encoding='unicode').replace('\n', '')
        )
        xml = xml_declaration + xml
        #print(">>>>", xml)
        # Faz o request com o servidor
        result = requests.post(url, xml, headers=mypost_header(), verify=False)
        result.encoding = 'utf-8'
        return result
    except requests.exceptions.RequestException as e:
        raise e
    finally:
        print("OK!")
        #certificado_a1.excluir()


#print(etree.tostring(xml))

#f = open("mylog.xml", "w")
#a = str(etree.tostring(xml))
#f.write(a)
#f.close()
#a1 = AssinaturaA1(certificado, "1234")
#xml = a1.assinar(xml)


def tarefa(tipo, xml=xml):

    if(tipo == 1):
        #'''
        certificado_a1 = CertificadoA1(certificado)
        chave, cert = certificado_a1.separar_arquivo(senha, caminho=True)
        chave_cert = (cert, chave)
        a1 = AssinaturaA1(certificado, senha)
        #XML DE ENVIO
        #f = open("xmlenvioOK.xml", "r")
        #XML DE RETORNO
        f = open("xmlok.xml", "r")
        xml = f.read()
        f.close()
        xml = etree.XML(xml)
        #xml = a1.assinar(xml)
        #print(xml)
        print(url)
        res = mdfe.post(xml, url, chave_cert)
        f = open("file.txt", "w")
        a = str(res.content)
        f.write(a)
        f.close()
        print(a)

        #'''

    elif (tipo == 2):
        certificado_a1 = CertificadoA1(certificado)
        chave, cert = certificado_a1.separar_arquivo(senha, caminho=True)
        chave_cert = (cert, chave)
        a1 = AssinaturaA1(certificado, senha)
        xml = a1.assinar(xml)
        res = mdfe.post(xml, url, chave_cert)
        f = open("xmlfuncional.xml", "w")
        f.write(str(etree.tostring(xml)))
        f.close()
        f = open("file.txt", "w")
        a = str(res.content)
        print(a)
        f.write(a)
        f.close()

tarefa(1)