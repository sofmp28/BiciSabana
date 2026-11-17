-- BiciSabana — Supabase/Postgres
-- Ejecutar UNA SOLA VEZ en un proyecto NUEVO desde SQL Editor.
-- Todas las tablas tienen RLS sin políticas para clientes públicos:
-- únicamente la API Python (service_role en el servidor) puede operar.

begin;

create table if not exists public.bicicletas (
  codigo text primary key check (length(trim(codigo)) > 0),
  color text not null check (length(trim(color)) > 0),
  fila smallint not null check (fila between 1 and 3),
  puesto smallint not null check (puesto between 1 and 10),
  estado text not null default 'Disponible'
    check (estado in ('Disponible', 'Prestada', 'En mantenimiento')),
  unique (fila, puesto)
);

-- Se conserva historial aunque después se retire la bicicleta.
create table if not exists public.prestamos (
  id bigint generated always as identity primary key,
  bicicleta text not null,
  estudiante char(6) not null check (estudiante ~ '^[0-9]{6}$'),
  fecha_inicio timestamptz not null default now(),
  fecha_fin timestamptz,
  activo boolean not null default true,
  duracion_minutos integer check (duracion_minutos is null or duracion_minutos >= 0),
  constraint cierre_consistente check (activo or fecha_fin is not null)
);

create unique index if not exists prestamo_activo_bici
  on public.prestamos (bicicleta) where activo;
create unique index if not exists prestamo_activo_est
  on public.prestamos (estudiante) where activo;
create index if not exists prestamo_fecha_idx on public.prestamos (fecha_inicio desc);

create table if not exists public.intentos_rechazados (
  id bigint generated always as identity primary key,
  fecha timestamptz not null default now(),
  bicicleta text,
  estudiante text,
  motivo text not null
);

-- Capacidad máxima: 3 x 10 puestos (30 bicicletas).
create or replace function public.limitar_30()
returns trigger language plpgsql security invoker set search_path = '' as $$
begin
  if (select count(*) from public.bicicletas) >= 30 then
    raise exception 'La estación solo admite 30 bicicletas.';
  end if;
  return new;
end;
$$;
drop trigger if exists trg_limitar_30 on public.bicicletas;
create trigger trg_limitar_30 before insert on public.bicicletas
for each row execute function public.limitar_30();

-- Un préstamo y el cambio de estado de su bicicleta se escriben juntos.
-- La transacción PostgreSQL revierte AMBOS si existe un conflicto de estudiante.
create or replace function public.prestar_bicicleta_atomico(
  p_bicicleta text, p_estudiante text, p_inicio timestamptz)
returns jsonb language plpgsql security invoker set search_path = '' as $$
declare v_reg public.prestamos%rowtype;
begin
  if p_estudiante !~ '^[0-9]{6}$' then
    raise exception 'El código estudiantil debe contener exactamente 6 números.';
  end if;
  update public.bicicletas set estado = 'Prestada'
    where codigo = p_bicicleta and estado = 'Disponible';
  if not found then
    raise exception 'La bicicleta no está disponible para prestar.';
  end if;
  insert into public.prestamos (bicicleta, estudiante, fecha_inicio, activo)
    values (p_bicicleta, p_estudiante, p_inicio, true)
    returning * into v_reg;
  return to_jsonb(v_reg);
end;
$$;

create or replace function public.devolver_bicicleta_atomico(
  p_bicicleta text, p_fin timestamptz, p_duracion integer)
returns jsonb language plpgsql security invoker set search_path = '' as $$
declare v_reg public.prestamos%rowtype;
begin
  if p_duracion < 0 then
    raise exception 'La duración no puede ser negativa.';
  end if;
  update public.prestamos set activo = false, fecha_fin = p_fin,
    duracion_minutos = p_duracion
    where bicicleta = p_bicicleta and activo = true
    returning * into v_reg;
  if not found then
    raise exception 'No existe préstamo activo de esa bicicleta.';
  end if;
  update public.bicicletas set estado = 'Disponible'
    where codigo = p_bicicleta and estado = 'Prestada';
  if not found then
    raise exception 'La bicicleta no tiene el estado Prestada.';
  end if;
  return to_jsonb(v_reg);
end;
$$;

-- Nunca conceder estas funciones a anon/authenticated: modifican datos.
revoke all on function public.prestar_bicicleta_atomico(text,text,timestamptz)
  from public, anon, authenticated;
revoke all on function public.devolver_bicicleta_atomico(text,timestamptz,integer)
  from public, anon, authenticated;
grant execute on function public.prestar_bicicleta_atomico(text,text,timestamptz)
  to service_role;
grant execute on function public.devolver_bicicleta_atomico(text,timestamptz,integer)
  to service_role;

alter table public.bicicletas enable row level security;
alter table public.prestamos enable row level security;
alter table public.intentos_rechazados enable row level security;
-- Acceso explícito para el backend con service_role (nunca clave pública).
grant all on public.bicicletas, public.prestamos, public.intentos_rechazados to service_role;
grant usage, select on all sequences in schema public to service_role;
revoke all on public.bicicletas, public.prestamos, public.intentos_rechazados from anon, authenticated;

-- Datos ficticios de demostración. Comentar este bloque si prefieres iniciar vacía.
insert into public.bicicletas (codigo, color, fila, puesto)
select 'B' || lpad(n::text,2,'0'),
  (array['Azul','Rojo','Verde','Amarillo','Negro','Blanco'])[((n-1)%6)+1],
  ((n-1)/10)+1, ((n-1)%10)+1
from generate_series(1,30) n
on conflict do nothing;

commit;
