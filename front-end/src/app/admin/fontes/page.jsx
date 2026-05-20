"use client";
import { useState, useEffect } from 'react';
import api from '../../../services/api';

export default function GestaoFontes() {
    const [cidades, setCidades] = useState([]);
    const [fontes, setFontes] = useState([]);
    const [form, setForm] = useState({ nome: '', url: '', tipo: 'RSS', cidade_id: '' });

    const carregarDados = () => {
        api.get('/admin/cidades_fontes').then(res => {
            setCidades(res.data.cidades);
            setFontes(res.data.fontes);
        });
    };

    useEffect(() => { carregarDados(); }, []);

    const salvarFonte = async (e) => {
        e.preventDefault();
        await api.post('/admin/fontes', form);
        setForm({ nome: '', url: '', tipo: 'RSS', cidade_id: '' });
        carregarDados();
        alert('Fonte cadastrada com sucesso!');
    };

    const excluirFonte = async (id) => {
        if(confirm('Tem certeza? Isso apagará também todas as notícias vinculadas a esta fonte!')) {
            await api.delete(`/admin/fontes/${id}`);
            carregarDados();
        }
    };

    return (
        <div className="row g-4">
            <div className="col-lg-4">
                <div className="card shadow-sm border-0">
                    <div className="card-header bg-primary text-white fw-bold">
                        <i className="bi bi-plus-circle me-2"></i>Nova Fonte
                    </div>
                    <div className="card-body">
                        <form onSubmit={salvarFonte}>
                            <div className="mb-3">
                                <label className="form-label small fw-bold">Nome do Portal</label>
                                <input type="text" className="form-control" value={form.nome} onChange={e => setForm({...form, nome: e.target.value})} required />
                            </div>
                            <div className="mb-3">
                                <label className="form-label small fw-bold">URL (Link do RSS ou Site)</label>
                                <input type="url" className="form-control" value={form.url} onChange={e => setForm({...form, url: e.target.value})} required />
                            </div>
                            <div className="mb-3">
                                <label className="form-label small fw-bold">Tipo de Raspagem</label>
                                <select className="form-select" value={form.tipo} onChange={e => setForm({...form, tipo: e.target.value})}>
                                    <option value="RSS">RSS Feed Oficial</option>
                                    <option value="HTML">Web Scraping (HTML)</option>
                                </select>
                            </div>
                            <div className="mb-4">
                                <label className="form-label small fw-bold">Cidade Foco (Opcional)</label>
                                <select className="form-select" value={form.cidade_id} onChange={e => setForm({...form, cidade_id: e.target.value})}>
                                    <option value="">Abrangência Regional (Várias)</option>
                                    {cidades.map(c => <option key={c.id} value={c.id}>{c.nome}</option>)}
                                </select>
                            </div>
                            <button type="submit" className="btn btn-primary w-100 fw-bold">Salvar Fonte</button>
                        </form>
                    </div>
                </div>
            </div>

            <div className="col-lg-8">
                <h4 className="fw-bold mb-3"><i className="bi bi-hdd-network text-primary me-2"></i>Fontes Cadastradas</h4>
                <div className="card shadow-sm border-0">
                    <div className="table-responsive">
                        <table className="table table-hover mb-0 align-middle">
                            <thead className="table-light">
                                <tr>
                                    <th>Nome</th>
                                    <th>URL / Tipo</th>
                                    <th>Cidade</th>
                                    <th className="text-end">Ações</th>
                                </tr>
                            </thead>
                            <tbody>
                                {fontes.map(f => (
                                    <tr key={f.id}>
                                        <td className="fw-bold">{f.nome}</td>
                                        <td>
                                            <a href={f.url} target="_blank" className="d-block small text-truncate" style={{maxWidth: '200px'}}>{f.url}</a>
                                            <span className="badge bg-secondary">{f.tipo}</span>
                                        </td>
                                        <td>{f.cidade_nome || <span className="text-muted fst-italic">Região</span>}</td>
                                        <td className="text-end">
                                            <button onClick={() => excluirFonte(f.id)} className="btn btn-sm btn-outline-danger">
                                                <i className="bi bi-trash"></i>
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
}