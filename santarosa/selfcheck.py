"""Ensayo automatizado de botones y evidencia reproducible del ejecutable."""
from pathlib import Path
from datetime import date
import tempfile,json
from .factory import ServiceFactory,seed_demo
from .ui import Desktop,DEMO_PASSWORD

def execute(root,output,screenshots=False):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    folder=Path(tempfile.mkdtemp(prefix='SantaRosa-check-'))
    s=ServiceFactory.create(folder/'check.srdb',DEMO_PASSWORD)
    seed_demo(s)
    app=Desktop(root,s,True);app.testing=True
    results=[]
    def check(name,condition):
        if not condition: raise AssertionError(name)
        results.append({'prueba':name,'resultado':'APROBADO'})
    def click(key): app.buttons[key].invoke();root.update()
    app.fields['patient_code'].set('P005');app.fields['patient_name'].set('Paciente ficticio cinco');click('register_patient')
    check('Botón registrar paciente',len(s.patients.search())==5)
    click('register_patient');check('Mensaje de paciente duplicado','Ya existe' in app.last_message)
    app.fields['search'].set('cinco');click('search_patient')
    check('Botón buscar',len(app.trees['patients'].get_children())==1)
    click('all_patients')
    app.fields['appointment_patient'].set('P005');app.fields['starts'].set(str(date.today())+' 15:00');click('schedule')
    check('Botón programar cita',len(s.agenda.list())==5)
    app.trees['appointments'].selection_set('4');app.fields['starts'].set(str(date.today())+' 15:30');click('reschedule')
    check('Botón reprogramar',s.agenda.list()[-1]['starts'].endswith('15:30'))
    click('cancel');check('Botón cancelar',s.agenda.list()[-1]['status']=='Cancelada')
    app.fields['attention_id'].set('4');click('attend')
    check('Botón registrar atención',len(s.agenda.attentions())==4)
    app.fields['lot'].set('L004');app.fields['product'].set('Medicamento ficticio D');click('register_lot')
    check('Botón registrar lote',len(s.inventory.list())==4)
    rows=app.row_values['lots'];idx=next(i for i,x in enumerate(rows) if x['code']=='L001')
    app.trees['lots'].selection_set(str(idx));app.fields['stock'].set('2');click('withdraw')
    check('Botón salida de 2 unidades',next(x for x in s.inventory.list() if x['code']=='L001')['stock']==18)
    app.fields['stock'].set('99');click('withdraw');check('Mensaje de stock insuficiente','Stock insuficiente' in app.last_message)
    app.fields['stock'].set('2');click('entry')
    check('Botón entrada',next(x for x in s.inventory.list() if x['code']=='L001')['stock']==20)
    click('alerts');check('Botón alertas',len(app.trees['alerts'].get_children())==2)
    click('report');check('Botón reporte',app.report_label.cget('text')=='4 atenciones en el periodo')
    s.reports.export(output/'reporte_demo.csv',str(date.today()),str(date.today()))
    s.repo.backup(output/'respaldo_demo.srdb')
    check('Exportación y respaldo', (output/'reporte_demo.csv').exists() and (output/'respaldo_demo.srdb').exists())
    if screenshots:
        from PIL import ImageGrab
        for label in ['Pacientes','Citas','Atenciones','Medicamentos','Alertas','Reportes']:
            app.notebook.select(app.tabs[label]);root.update();root.after(250);root.update()
            import ctypes
            hwnd=ctypes.windll.user32.GetParent(root.winfo_id())
            ImageGrab.grab(window=hwnd).save(output/(label.lower()+'.png'))
    app.close()
    reopened=ServiceFactory.create(folder/'check.srdb',DEMO_PASSWORD)
    check('Persistencia después de cerrar',len(reopened.patients.search())==5 and len(reopened.agenda.attentions())==4)
    reopened.close()
    import sys,platform
    (output/'resultado_ejecutable.json').write_text(json.dumps({'ejecutable_empaquetado':bool(getattr(sys,'frozen',False)),'python':platform.python_version(),'sistema':platform.platform(),'pruebas':results},ensure_ascii=False,indent=2),encoding='utf-8')
