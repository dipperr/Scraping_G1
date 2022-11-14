from bs4 import BeautifulSoup
import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from time import perf_counter
import warnings

warnings.filterwarnings('ignore')


class Site:
    """
    Define a estutura base do site do g1.globo.
    Tanto da página principal quanto das páginas
    de artigos
    """

    def __init__(self, main, a, h1, h2, p):
        self._main = main
        self._a = a
        self._h1 = h1
        self._h2 = h2
        self._p = p

    @property
    def main(self):
        return self._main

    @property
    def a(self):
        return self._a

    @property
    def h1(self):
        return self._h1

    @property
    def h2(self):
        return self._h2

    @property
    def p(self):
        return self._p


class Noticia:
    """
    Define a estrutura da pagina inicial do site do g1.globo.com
    """

    def __init__(self, url, titulo):
        self._titulo = titulo
        self._url = url
        self._hashe = hash(url)

    @property
    def titulo(self):
        return self._titulo

    @property
    def url(self):
        return self._url

    @property
    def hashe(self):
        return self._hashe

    def __eq__(self, outro):
        return self.hashe == outro.hashe

    def __str__(self):
        return "URL: {0}\nTITULO: {1}\n".format(self.url, self.titulo)


class Artigo:
    """
    Define a estrutura das paginas de artigos do site do g1.globo.com
    """

    def __init__(self, url, titulo, subtitulo, data):
        self._url = url
        self._titulo = titulo
        self._subtitulo = subtitulo
        self._data = data
        self._hashe = hash(url)

    @property
    def url(self):
        return self._url

    @property
    def titulo(self):
        return self._titulo

    @property
    def subtitulo(self):
        return self._subtitulo

    @property
    def data(self):
        return self._data

    @property
    def hashe(self):
        return self._hashe

    def __eq__(self, outro):
        return self.hashe == outro.hashe

    def __str__(self):
        return "URL: {0}\nTITLE: {1}\nSUB: {2}\nDATA: {3}".format(self.url, self.titulo, self.subtitulo, self.data)


class Crawler:
    def __init__(self, site_obj):
        self._site = site_obj
        self._chromeOptions = Options()
        self._chromeOptions.add_argument('--headless')
        self._driver = 'chromedriver'
        self._artigos = []
        self._noticias = []

    def get_page(self, url):
        driver = webdriver.Chrome(executable_path=self._driver, chrome_options=self._chromeOptions)
        driver.get(url)
        time.sleep(3)
        return BeautifulSoup(driver.page_source, 'html.parser')

    def get_artigo(self, url):
        artigo_html = requests.get(url)
        artigo_html.raise_for_status()
        bs_artigo = BeautifulSoup(artigo_html.text, 'html.parser')
        try:
            titulo = bs_artigo.find('h1', self._site.h1).get_text()
            sub = bs_artigo.find('h2', self._site.h2).get_text()
            data = bs_artigo.find('p', self._site.p).time['datetime']
        except AttributeError:
            print('Não foi possivel achar os atributos na seguite url:!!!')
            print(url)
            print()
            return None
        else:
            artigo = Artigo(url, titulo, sub, data)
            return artigo

    def scraping(self, url):
        bs_object = self.get_page(url)
        for a in bs_object.find('main', self._site.main).find_all('a', self._site.a):
            if re.search('^(https://g1.globo.com/index).*', a['href']) is None:
                noticia = Noticia(a['href'], a.get_text())
                if noticia not in self._noticias:
                    self._noticias.append(noticia)
                    artigo = self.get_artigo(noticia.url)
                    if artigo is not None:
                        print(artigo)
                        print()
                        self._artigos.append(artigo)
            else:
                r1 = input('deseja seguir o link[s/n]: {}'.format(a['href']))
                if r1.lower().strip() == 's':
                    self.scraping(a['href'])

    @property
    def artigos(self):
        return self._artigos

    @property
    def noticias(self):
        return self._noticias


attrs = {
    'main': {'id': 'glb-main-home'},
    'a': {'href': re.compile('^(https://g1.globo.com).*')},
    'h1': {'class': 'content-head__title'},
    'h2': {'class': 'content-head__subtitle'},
    'p': {'class': 'content-publication-data__updated'}
}

site = Site(**attrs)
crawler = Crawler(site)
crawler.scraping('https://g1.globo.com')
