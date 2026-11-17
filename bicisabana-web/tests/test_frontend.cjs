const fs=require('fs');
const vm=require('vm');
const html=fs.readFileSync(__dirname+'/../public/index.html','utf8');
const found=html.match(/<script[^>]*data-dc-script[^>]*>([\s\S]*?)<\/script>/);
if(!found)throw new Error('Falta el código de la interfaz.');
const ctx={console,Date,setTimeout,clearTimeout,setInterval,clearInterval,Math,JSON,
 DCLogic:class{setState(v){Object.assign(this.state,v)}}};
vm.createContext(ctx);
vm.runInContext(found[1]+';globalThis.testComponent=Component;globalThis.testOps=Ops;',ctx);
const c=new ctx.testComponent();
const examples={prestar:["B01","123456"],devolver:["B01"],registrar:[{codigo:"B31",fila:"3",puesto:"10",color:"Verde"}],mantenimiento:["B01"],reactivar:["B01"],mover:["B01",3,5],retirar:["B01"],cargarEjemplo:[]};
const paths={prestar:'/api/prestamos',devolver:'/api/devoluciones',registrar:'/api/bicicletas',mantenimiento:'/api/mantenimiento',reactivar:'/api/reactivar',mover:'/api/mover',retirar:'/api/retirar',cargarEjemplo:'/api/cargar-ejemplo'};
for(const name of Object.keys(paths)){
 const v=c.capture(dd=>ctx.testOps[name](dd,...examples[name]));
 if(v.path!==paths[name])throw new Error('Ruta incorrecta: '+name);
 console.log('OK',name,v.path);
}
const state=c.adaptRemote({bicicletas:[{codigo:'B01',fila:1,puesto:1}],prestamos:[{id:1,fecha_inicio:'2026-11-16T12:00:00Z',fecha_fin:null,activo:true}],rechazos:[]});
if(state.prestamos[0].inicio!=='2026-11-16T12:00:00Z')throw new Error('Fechas no adaptadas');
console.log('OK: ocho rutas y mapeo de fechas correctamente vinculados.');
