"use client";
import { useState, useEffect } from 'react';
import Link from 'next/link';
import api from '../../../services/api';

export default function GestaoUsuarios() {
    const [usuarios, setUsuarios] = useState([]);

    const carregarUsuarios = () => {
        api.get('/admin/usuarios').then(res => setUsuarios(res.data));
    };

    useEffect(() => { carregarUsuarios(); }, []);

    const toggleBloqueio = async (id) => {
        if(confirm('Tem certeza que deseja alterar o status deste usuário?')){
            await api.post(`/admin/usuarios/${id}/bloquear`);
            carregarUsuarios();
        }
    };

    const toggleCargo = async (id) => {
        if(confirm('Tem certeza que deseja alterar os privilégios deste usuário?')){
            await api.post(`/admin/usuarios/${id}/cargo`);
            carregarUsuarios();
        }
    };

    return (
        <div>
            <h3 className="fw-bold mb-4"><i className="bi bi-people-fill text-primary me-2"></i> Gestão de Usuários</h3>
            <div className="card shadow-sm border-0">
                <div className="table-responsive">
                    <table className="table table-hover mb-0 align-middle">
                        <thead className="table-light">
                            <tr><th>ID</th><th>Nome</th><th>E-mail</th><th>Cargo</th><th>Status</th><th className="text-end">Ações</th></tr>
                        </thead>
                        <tbody>
                            {usuarios.map(u => (
                                <tr key={u.id}>
                                    <td>#{u.id}</td>
                                    <td className="fw-bold">{u.nome}</td>
                                    <td>{u.email}</td>
                                    <td><span className={`badge ${u.role === 'admin' ? 'bg-primary' : 'bg-secondary'}`}>{u.role.toUpperCase()}</span></td>
                                    <td><span className={`badge ${u.ativo ? 'bg-success' : 'bg-danger'}`}>{u.ativo ? 'Ativo' : 'Bloqueado'}</span></td>
                                    <td className="text-end">
                                        <Link href={`/admin/usuarios/editar/${u.id}`} className="btn btn-sm btn-outline-info me-2" title="Editar">
                                            <i className="bi bi-pencil"></i>
                                        </Link>
                                        <button onClick={() => toggleCargo(u.id)} className="btn btn-sm btn-outline-primary me-2" title="Alterar Cargo">
                                            <i className="bi bi-arrow-repeat"></i>
                                        </button>
                                        <button onClick={() => toggleBloqueio(u.id)} className={`btn btn-sm ${u.ativo ? 'btn-outline-danger' : 'btn-outline-success'}`}>
                                            <i className={`bi ${u.ativo ? 'bi-lock-fill' : 'bi-unlock-fill'}`}></i> {u.ativo ? 'Bloquear' : 'Desbloquear'}
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}