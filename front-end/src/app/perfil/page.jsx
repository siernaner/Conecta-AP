"use client";
import { useContext, useState, useEffect } from 'react';
import { AuthContext } from '../../contexts/AuthContext';
import api from '../../services/api';

export default function Perfil() {
    const { user, setUser, signOut } = useContext(AuthContext);
    const [form, setForm] = useState({ nome: '', email: '', senha: '' });
    const [msg, setMsg] = useState('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (user && user.id) {
            api.get(`/usuario/${user.id}`).then(res => {
                setForm({ nome: res.data.nome, email: res.data.email, senha: '' });
            }).catch(err => console.error(err));
        }
    }, [user]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const data = {};
            if (form.nome !== user.nome) data.nome = form.nome;
            if (form.email !== user.email) data.email = form.email;
            if (form.senha) data.senha = form.senha;
            if (Object.keys(data).length === 0) {
                setMsg('Nenhuma alteração');
                setLoading(false);
                return;
            }
            await api.put(`/usuario/${user.id}`, data);
            if (data.nome) {
                setUser({ ...user, nome: data.nome });
                localStorage.setItem('nome', data.nome);
            }
            if (data.email) localStorage.setItem('email', data.email);
            setMsg('Dados atualizados com sucesso!');
            setForm(prev => ({ ...prev, senha: '' }));
        } catch (err) {
            setMsg(err.response?.data?.erro || 'Erro ao atualizar');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container py-4">
            <h2>Meu Perfil</h2>
            {msg && <div className="alert alert-info">{msg}</div>}
            <form onSubmit={handleSubmit}>
                <div className="mb-3">
                    <label className="form-label">Nome</label>
                    <input type="text" className="form-control" value={form.nome} onChange={e => setForm({...form, nome: e.target.value})} required />
                </div>
                <div className="mb-3">
                    <label className="form-label">E-mail</label>
                    <input type="email" className="form-control" value={form.email} onChange={e => setForm({...form, email: e.target.value})} required />
                </div>
                <div className="mb-3">
                    <label className="form-label">Nova senha (deixe em branco para manter)</label>
                    <input type="password" className="form-control" value={form.senha} onChange={e => setForm({...form, senha: e.target.value})} />
                    <small className="text-muted">Mínimo 8 caracteres, com maiúscula, minúscula e número</small>
                </div>
                <button type="submit" className="btn btn-primary" disabled={loading}>Salvar</button>
            </form>
        </div>
    );
}