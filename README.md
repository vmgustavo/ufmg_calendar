##Modo de uso
1. Instalar bibliotecas do Python necessárias listadas no arquivo reqs.txt
    * Testado com o Python 3.5.4
2. Executar 'calendar_read.py' (janela do Chrome irá abrir para leitura dos dados do site do calendário da UFMG)
    * Possível editar se deseja salvar somente feriados e recessos ou todos os eventos pelo valor da variável 'feriado_only' (estado atual salva somente feriados).
3. Usar o arquivo 'ufmg_calendar.csv' e importar para alguma agenda do Google Calendar

##Possível problema
* Se o 'chromedriver.exe' não funcionar ou não for suficiente para execução baixar o driver neste [link][chrome-driver], substituir pelo atual na pasta de execução e manter o mesmo nome.


[chrome-driver]: http://chromedriver.chromium.org/
