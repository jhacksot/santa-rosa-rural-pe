"""Reportes agregados exportables sin nombres ni identificadores de pacientes."""
import csv
from collections import Counter
from .domain import day,ValidationError
from .repository import Repository

class ReportService:
    def __init__(self,repo:Repository): self.repo=repo
    def summarize(self,start,end):
        if day(start)>day(end): raise ValidationError('La fecha inicial supera a la final.')
        rows=self.repo.rows('SELECT area FROM attentions WHERE attended BETWEEN ? AND ?',(start,end))
        counts=Counter(map(lambda row:row['area'],rows))
        return {'start':start,'end':end,'total':len(rows),'areas':dict(sorted(counts.items()))}
    def export(self,path,start,end):
        data=self.summarize(start,end)
        with open(path,'w',newline='',encoding='utf-8-sig') as f:
            writer=csv.writer(f)
            writer.writerow(['Inicio','Fin','Area','Atenciones'])
            for area,count in data['areas'].items():
                # Neutraliza fórmulas si se abre el CSV en Excel.
                safe="'"+area if area.lstrip().startswith(('=','+','-','@')) else area
                writer.writerow([start,end,safe,count])
            writer.writerow([start,end,'TOTAL',data['total']])
        return data
