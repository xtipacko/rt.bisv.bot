#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
# Equivalency maps module

TICKET_STATUS= {
                 'created' : 'Сдана монтажом',
                 'active'  : 'Принята в работу', 
                 'solved'  : 'Решена'
                }
STATUS_REPORTS = {
                 'created' : ('создан',),
                 'active'  : ('принят', 'в работе','принял', 'ок'), 
                 'solved'  : ('решен', 'готов', 'сделан', '+', 'выполн', 'есть')
                }
# Отчет о состоянии заявки принятый от тех поддержки