"""Interfaz de escritorio por eventos. Los botones delegan en servicios."""
from datetime import date,timedelta
from pathlib import Path
import os
import tempfile
import tkinter as tk
from tkinter import ttk,messagebox,filedialog
from .domain import ValidationError
from .factory import ServiceFactory,seed_demo

DEMO_PASSWORD='SantaRosa-Demo-2026'

class Desktop:
    def __init__(self,root,service=None,demo=False):
        self.root,self.service,self.demo=root,service,demo
        self.last_message=''
        self.testing=False
        root.title('Santa Rosa · Sistema Rural-PE')
        root.geometry('1160x720');root.minsize(1050,650)
        root.configure(bg='#f4f7f8')
        style=ttk.Style(root);style.theme_use('clam')
        style.configure('.',font=('Segoe UI',11),background='#f4f7f8',foreground='#18343a')
        style.configure('TButton',padding=(12,8))
        style.configure('Accent.TButton',background='#087e83',foreground='white')
        style.map('Accent.TButton',background=[('active','#075d62')])
        style.configure('Treeview',rowheight=27,background='white',fieldbackground='white',font=('Segoe UI',10))
        style.configure('Treeview.Heading',font=('Segoe UI',10,'bold'),background='#e1ecee')
        style.configure('TNotebook.Tab',padding=(14,10))
        self.status=tk.StringVar(value='Listo')
        root.protocol('WM_DELETE_WINDOW',self.close)
        self.login() if service is None else self.build()

    def clear(self):
        for child in self.root.winfo_children(): child.destroy()
    def login(self):
        self.clear()
        frame=ttk.Frame(self.root,padding=50);frame.pack(expand=True)
        ttk.Label(frame,text='SANTA ROSA',font=('Segoe UI',30,'bold')).pack(anchor='w')
        ttk.Label(frame,text='Sistema Rural-PE',font=('Segoe UI',20)).pack(anchor='w',pady=(0,24))
        ttk.Label(frame,text='Prototipo académico · Solo datos ficticios\nPacientes, citas, atenciones y medicamentos',font=('Segoe UI',13)).pack(anchor='w',pady=(0,24))
        ttk.Button(frame,text='Abrir demostración con datos de ejemplo',style='Accent.TButton',command=lambda:self.run(self.open_demo)).pack(fill='x',pady=8)
        ttk.Label(frame,text='La demostración crea una sesión nueva en cada apertura.').pack(anchor='w',pady=(0,24))
        self.password=tk.StringVar()
        ttk.Label(frame,text='Contraseña de tu práctica guardada (mínimo 10 caracteres)').pack(anchor='w')
        entry=ttk.Entry(frame,textvariable=self.password,show='•',width=48);entry.pack(fill='x',pady=8)
        ttk.Button(frame,text='Crear o abrir mi práctica',command=lambda:self.run(self.open_practice)).pack(fill='x')
        ttk.Button(frame,text='Abrir respaldo cifrado...',command=lambda:self.run(self.open_backup)).pack(fill='x',pady=8)
        ttk.Label(frame,text='La primera apertura crea la práctica. Conserva tu contraseña:\nno hay recuperación de contraseña ni almacenamiento en la nube.',font=('Segoe UI',10)).pack(anchor='w',pady=12)
    def open_demo(self):
        folder=Path(tempfile.mkdtemp(prefix='SantaRosa-demo-'))
        self.service=ServiceFactory.create(folder/'demo.srdb',DEMO_PASSWORD)
        seed_demo(self.service);self.demo=True;self.build()
    def open_practice(self):
        folder=Path(os.environ.get('LOCALAPPDATA',str(Path.home()))) / 'SantaRosaAcademico'
        self.service=ServiceFactory.create(folder/'practica.srdb',self.password.get())
        self.demo=False;self.build()
    def open_backup(self):
        path=filedialog.askopenfilename(title='Abrir copia cifrada con la contraseña indicada',filetypes=[('Base Santa Rosa','*.srdb')])
        if path:
            self.service=ServiceFactory.create(path,self.password.get());self.demo=False;self.build()
    def run(self,action):
        try:
            action()
            self.last_message='Operación completada.'
            self.status.set(self.last_message)
            if self.service and hasattr(self,'trees'): self.refresh()
        except (ValidationError,OSError) as exc:
            self.last_message=str(exc);self.status.set(self.last_message)
            if not self.testing: messagebox.showwarning('Revisar datos',str(exc),parent=self.root)
        except Exception as exc:
            self.last_message='No se completó la operación. '+type(exc).__name__
            self.status.set(self.last_message)
            if not self.testing: messagebox.showerror('Operación no completada',self.last_message,parent=self.root)
    def build(self):
        self.clear();self.fields={};self.trees={};self.buttons={};self.row_values={}
        header=ttk.Frame(self.root,padding=(22,16));header.pack(fill='x')
        ttk.Label(header,text='Santa Rosa',font=('Segoe UI',25,'bold')).pack(side='left')
        ttk.Label(header,text='  Sistema Rural-PE  /  Solo datos ficticios',font=('Segoe UI',12)).pack(side='left')
        ttk.Button(header,text='Cerrar sesión',command=self.logout).pack(side='right')
        ttk.Button(header,text='Respaldo cifrado',command=lambda:self.run(self.backup)).pack(side='right',padx=10)
        label='DEMOSTRACIÓN · Sesión temporal con datos de ejemplo' if self.demo else 'PRÁCTICA GUARDADA · Cambios cifrados después de cada operación'
        ttk.Label(self.root,text=label,foreground='#087e83',padding=(24,0,0,12),font=('Segoe UI',11,'bold')).pack(anchor='w')
        ttk.Label(self.root,textvariable=self.status,padding=(22,10),font=('Segoe UI',10)).pack(side='bottom',fill='x')
        self.notebook=ttk.Notebook(self.root);self.notebook.pack(fill='both',expand=True,padx=22,pady=4)
        tabs={}
        for name in ['Pacientes','Citas','Atenciones','Medicamentos','Alertas','Reportes']:
            tabs[name]=ttk.Frame(self.notebook,padding=16);self.notebook.add(tabs[name],text=name)
        self.tabs=tabs
        self.form(tabs['Pacientes'],[('patient_code','Código','P005'),('patient_name','Nombre ficticio',''),('search','Buscar','')])
        self.actions(tabs['Pacientes'],[
            ('register_patient','Registrar paciente',lambda:self.service.patients.register(self.value('patient_code'),self.value('patient_name'))),
            ('search_patient','Buscar',lambda:None),('all_patients','Ver todos',lambda:self.fields['search'].set(''))])
        self.tree(tabs['Pacientes'],'patients',[('code','Código',120),('name','Nombre ficticio',500)])
        today=date.today().isoformat()
        self.form(tabs['Citas'],[('appointment_patient','Código de paciente','P004'),('professional','Profesional ficticio','Profesional de demostración'),('starts','Fecha y hora',today+' 15:00')])
        ttk.Label(tabs['Citas'],text='Formato AAAA-MM-DD HH:MM · Turnos de 30 minutos (00 o 30). Para reprogramar, seleccione una cita y cambie la fecha.').pack(anchor='w',pady=5)
        self.actions(tabs['Citas'],[
            ('schedule','Programar cita',lambda:self.service.agenda.schedule(self.value('appointment_patient'),self.value('professional'),self.value('starts'))),
            ('reschedule','Reprogramar seleccionada',lambda:self.service.agenda.reschedule(self.selected('appointments'),self.value('starts'))),
            ('cancel','Cancelar seleccionada',lambda:self.service.agenda.cancel(self.selected('appointments')))])
        self.tree(tabs['Citas'],'appointments',[('id','N.º',65),('patient','Paciente',110),('professional','Profesional ficticio',230),('starts','Fecha y hora',180),('status','Estado',130)])
        self.form(tabs['Atenciones'],[('attention_id','N.º de cita','4'),('area','Área','Medicina general')])
        ttk.Label(tabs['Atenciones'],text='Registro administrativo. No ingrese diagnósticos, DNI, teléfonos ni historias clínicas.').pack(anchor='w',pady=8)
        self.actions(tabs['Atenciones'],[('attend','Registrar atención',lambda:self.service.agenda.attend(self.value('attention_id'),self.value('area')))])
        self.tree(tabs['Atenciones'],'attentions',[('id','N.º',65),('patient','Paciente',120),('professional','Profesional ficticio',240),('attended','Fecha',140),('area','Área',180)])
        self.form(tabs['Medicamentos'],[('lot','Lote','L004'),('product','Medicamento ficticio',''),('expires','Vencimiento',(date.today()+timedelta(days=365)).isoformat()),('stock','Unidades','20')])
        self.actions(tabs['Medicamentos'],[
            ('register_lot','Registrar nuevo lote',lambda:self.service.inventory.register(self.value('lot'),self.value('product'),self.value('expires'),self.value('stock'))),
            ('entry','Entrada a seleccionado',lambda:self.service.inventory.move(self.selected('lots'),self.value('stock'),'Entrada')),
            ('withdraw','Salida de seleccionado',lambda:self.service.inventory.move(self.selected('lots'),self.value('stock'),'Salida'))])
        ttk.Label(tabs['Medicamentos'],text='Para un movimiento, seleccione el lote y escriba la cantidad en Unidades. No se registran ventas ni importes.').pack(anchor='w',pady=5)
        self.tree(tabs['Medicamentos'],'lots',[('code','Lote',100),('product','Medicamento ficticio',300),('expires','Vencimiento',150),('stock','Stock',100)],height=4)
        ttk.Label(tabs['Medicamentos'],text='Historial de movimientos',font=('Segoe UI',11,'bold')).pack(anchor='w',pady=(10,2))
        self.tree(tabs['Medicamentos'],'movements',[('id','N.º',65),('lot','Lote',100),('kind','Movimiento',170),('amount','Unidades',110),('created','Fecha',150)],height=3)
        self.form(tabs['Alertas'],[('threshold','Stock mínimo','5'),('horizon','Días de anticipación','30')])
        self.actions(tabs['Alertas'],[('alerts','Actualizar alertas',lambda:self.service.inventory.alerts(self.value('threshold'),self.value('horizon')))])
        self.tree(tabs['Alertas'],'alerts',[('code','Lote',100),('product','Medicamento ficticio',250),('expires','Vencimiento',140),('stock','Stock',80),('alert','Alerta',250)])
        self.form(tabs['Reportes'],[('start','Desde',today),('end','Hasta',today)])
        self.actions(tabs['Reportes'],[('report','Consultar periodo',self.update_report),('csv','Exportar CSV',self.export_csv)])
        self.report_label=ttk.Label(tabs['Reportes'],text='',font=('Segoe UI',20,'bold'));self.report_label.pack(anchor='w',pady=16)
        self.tree(tabs['Reportes'],'report',[('area','Área',400),('count','Atenciones',150)])
        ttk.Label(tabs['Reportes'],text='El reporte exporta únicamente cantidades por área. Incluye ambos extremos del periodo.').pack(anchor='w',pady=10)
        self.refresh()
    def form(self,parent,fields):
        frame=ttk.Frame(parent);frame.pack(fill='x',pady=(0,8))
        for i,(key,label,default) in enumerate(fields):
            frame.columnconfigure(i,weight=1)
            ttk.Label(frame,text=label).grid(row=0,column=i,sticky='w',padx=(0,12))
            var=tk.StringVar(value=default);self.fields[key]=var
            ttk.Entry(frame,textvariable=var,width=20).grid(row=1,column=i,sticky='ew',padx=(0,12),pady=6)
    def actions(self,parent,actions):
        frame=ttk.Frame(parent);frame.pack(fill='x',pady=(2,10))
        for i,(key,label,action) in enumerate(actions):
            button=ttk.Button(frame,text=label,style='Accent.TButton' if i==0 else 'TButton',command=lambda action=action:self.run(action))
            button.pack(side='left',padx=(0,8));self.buttons[key]=button
    def tree(self,parent,key,columns,height=10):
        frame=ttk.Frame(parent);frame.pack(fill='both',expand=True)
        tree=ttk.Treeview(frame,columns=[c[0] for c in columns],show='headings',height=height,selectmode='browse')
        for name,label,width in columns:
            tree.heading(name,text=label);tree.column(name,width=width,minwidth=50)
        scrollbar=ttk.Scrollbar(frame,orient='vertical',command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side='left',fill='both',expand=True);scrollbar.pack(side='right',fill='y');self.trees[key]=tree
    def value(self,key): return self.fields[key].get().strip()
    def selected(self,key):
        ids=self.trees[key].selection()
        if not ids: raise ValidationError('Seleccione una fila de la tabla.')
        return self.row_values[key][int(ids[0])][self.trees[key]['columns'][0]]
    def fill(self,key,rows):
        tree=self.trees[key];selected=tree.selection()
        self.row_values[key]=rows
        tree.delete(*tree.get_children())
        columns=tree['columns']
        for i,row in enumerate(rows): tree.insert('',tk.END,iid=str(i),values=[row[c] for c in columns])
        if selected and tree.exists(selected[0]): tree.selection_set(selected[0])
    def refresh(self):
        self.fill('patients',self.service.patients.search(self.value('search')))
        self.fill('appointments',self.service.agenda.list())
        self.fill('attentions',self.service.agenda.attentions())
        self.fill('lots',self.service.inventory.list())
        self.fill('movements',self.service.inventory.movements())
        try: self.fill('alerts',self.service.inventory.alerts(self.value('threshold'),self.value('horizon')))
        except ValidationError: self.fill('alerts',[])
        try: self.update_report()
        except ValidationError:
            self.report_label.configure(text='Revise el periodo del reporte')
            self.fill('report',[])
    def update_report(self):
        data=self.service.reports.summarize(self.value('start'),self.value('end'))
        self.report_label.configure(text=f"{data['total']} atenciones en el periodo")
        self.fill('report',[{'area':a,'count':n} for a,n in data['areas'].items()])
    def export_csv(self):
        path=filedialog.asksaveasfilename(defaultextension='.csv',initialfile='reporte_santa_rosa.csv',filetypes=[('CSV','*.csv')])
        if path: self.service.reports.export(path,self.value('start'),self.value('end'))
    def backup(self):
        path=filedialog.asksaveasfilename(defaultextension='.srdb',initialfile='respaldo_santa_rosa.srdb',filetypes=[('Base cifrada','*.srdb')])
        if path: self.service.repo.backup(path)
    def logout(self):
        self.service.close();self.service=None
        if hasattr(self,'trees'): del self.trees
        self.login()
    def close(self):
        if self.service: self.service.close()
        self.root.destroy()
