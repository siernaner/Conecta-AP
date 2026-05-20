"use client";
import { useState, useEffect } from 'react';
import api from '../../../services/api';

export default function ModeracaoNoticias() {
    const [noticias, setNoticias] = useState([]);

    const carregarNoticias = () => {
        api.get('/admin/moderacao').then(res => setNoticias(res.data));
    };

    useEffect(() => { carregarNoticias(); }, []);

    const toggleVisibilidade = async (id, oculto) => {
        const acao = oculto ? 'mostrar' : 'ocultar';
        if(confirm(`Tem certeza que deseja ${acao} esta notícia no feed principal?`)) {
            await api.post(`/admin/noticias/${id}/toggle`);
            carregarNoticias();
        }
    };

    return (
        <div>
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h3 className="fw-bold m-0"><i className="bi bi-shield-check text-primary me-2"></i> Moderação de Feed</h3>
                <span className="badge bg-secondary">Últimas 100 inserções</span>
            </div>
            
            <div className="card shadow-sm border-0">
                <div className="table-responsive">
                    <table className="table table-hover mb-0 align-middle">
                        <thead className="table-light">
                            <tr>
                                <th>Data</th>
                                <th>Título</th>
                                <th>Status</th>
                                <th>Fonte / Cidade</th>
                                <th className="text-end">Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {noticias.map(n => (
                                <tr key={n.id} className={n.oculto ? 'table-secondary text-muted opacity-75' : ''}>
                                    <td className="small">{new Date(n.data_publicacao).toLocaleDateString('pt-BR')}</td>
                                    <td className="fw-bold" style={{maxWidth: '350px'}}>{n.titulo}</td>
                                    <td>
                                        {n.oculto ? (
                                            <span className="badge bg-secondary"><i className="bi bi-eye-slash-fill me-1"></i> Oculta</span>
                                        ) : (
                                            <span className="badge bg-success"><i className="bi bi-eye-fill me-1"></i> Visível</span>
                                        )}
                                    </td>
                                    <td>
                                        <span className="d-block small">{n.fonte_nome}</span>
                                        <span className={`badge ${n.oculto ? 'bg-secondary' : 'bg-info-subtle text-info-emphasis'}`}>
                                            {n.cidade}
                                        </span>
                                    </td>
                                    <td className="text-end">
                                        <button 
                                            onClick={() => toggleVisibilidade(n.id, n.oculto)} 
                                            className={`btn btn-sm ${n.oculto ? 'btn-outline-success' : 'btn-outline-warning'}`} 
                                            title={n.oculto ? 'Restaurar Notícia' : 'Ocultar Notícia'}
                                        >
                                            {n.oculto ? (
                                                <><i className="bi bi-eye-fill"></i> Mostrar</>
                                            ) : (
                                                <><i className="bi bi-eye-slash-fill"></i> Ocultar</>
                                            )}
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