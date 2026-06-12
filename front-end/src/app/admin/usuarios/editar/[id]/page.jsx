"use client";
import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import api from '@/services/api';  // ← alias correto

export default function EditarUsuario() {
    const { id } = useParams();
    const router = useRouter();
    const [form, setForm] = useState({ nome: '', email: '', senha: '' });
    const [msg, setMsg] = useState('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        api.get(`/usuario/${id}`).then(res => {
            setForm({ nome: res.data.nome, email: res.data.email, senha: '' });
        }).catch(err => console.error(err));
    }, [id]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const data = {};
            if (form.nome) data.nome = form.nome;
            if (form.email) data.email = form.email;
            if (form.senha) data.senha = form.senha;
            await api.put(`/usuario/${id}`, data);
            setMsg('Usuário atualizado com sucesso!');
            setTimeout(() => router.push('/admin/usuarios'), 2000);
        } catch (err) {
            setMsg(err.response?.data?.erro || 'Erro ao atualizar');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container py-4">
            <h2 className="mb-4">Editar Usuário</h2>
            {msg && <div className="alert alert-info">{msg}</div>}
            <form onSubmit={handleSubmit} className="card p-4">
                <div className="mb-3">
                    <label className="form-label fw-bold">Nome</label>
                    <input type="text" className="form-control" value={form.nome} onChange={e => setForm({...form, nome: e.target.value})} required />
                </div>
                <div className="mb-3">
                    <label className="form-label fw-bold">E-mail</label>
                    <input type="email" className="form-control" value={form.email} onChange={e => setForm({...form, email: e.target.value})} required />
                </div>
                <div className="mb-4">
                    <label className="form-label fw-bold">Nova senha <span className="text-muted">(opcional)</span></label>
                    <input type="password" className="form-control" value={form.senha} onChange={e => setForm({...form, senha: e.target.value})} />
                    <small className="text-muted">Mínimo 8 caracteres, com letra maiúscula, minúscula e número.</small>
                </div>
                <div className="d-flex gap-2">
                    <button type="submit" className="btn btn-primary" disabled={loading}>
                        {loading ? 'Salvando...' : 'Salvar alterações'}
                    </button>
                    <button type="button" className="btn btn-secondary" onClick={() => router.back()}>Cancelar</button>
                </div>
            </form>
        </div>
    );
}