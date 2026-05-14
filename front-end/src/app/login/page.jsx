"use client";
import { useState, useContext } from 'react';
import { AuthContext } from '../../contexts/AuthContext';
import api from '../../services/api';

export default function Login() {
    const { signIn } = useContext(AuthContext);
    const [isLogin, setIsLogin] = useState(true); // Controla se estamos na tela de Login ou Cadastro
    
    const [nome, setNome] = useState('');
    const [email, setEmail] = useState('');
    const [senha, setSenha] = useState('');
    
    const [erro, setErro] = useState('');
    const [sucesso, setSucesso] = useState('');
    const [carregando, setCarregando] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErro('');
        setSucesso('');
        setCarregando(true);

        if (isLogin) {
            // --- FLUXO DE LOGIN ---
            try {
                await signIn(email, senha);
            } catch (error) {
                setErro("Credenciais Inválidas."); // Mensagem neutra por segurança
            }
        } else {
            // --- FLUXO DE CADASTRO ---
            try {
                await api.post('/registro', { nome, email, senha });
                setSucesso("Conta criada com sucesso! Faça o login.");
                setIsLogin(true); // Volta para a tela de login
                setSenha(''); // Limpa a senha por segurança
            } catch (error) {
                if (error.response?.data?.erro === 'senha_fraca') {
                    setErro("A senha não atende aos requisitos de segurança.");
                } else {
                    setErro("Erro ao cadastrar. O e-mail pode já estar em uso.");
                }
            }
        }
        setCarregando(false);
    };

    return (
        <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '80vh' }}>
            <div className="card shadow-sm border-0" style={{ width: '100%', maxWidth: '450px' }}>
                <div className="card-header bg-white text-center py-4 border-0">
                    <h3 className="fw-bold text-primary mb-1">
                        {isLogin ? 'Acesso Seguro' : 'Criar Conta'}
                    </h3>
                    <p className="text-muted small mb-0">
                        Autenticação protegida por Bcrypt e JWT
                    </p>
                </div>
                
                <div className="card-body px-4 pb-4">
                    {/* Alertas de Erro e Sucesso */}
                    {erro && <div className="alert alert-danger py-2">{erro}</div>}
                    {sucesso && <div className="alert alert-success py-2">{sucesso}</div>}

                    <form onSubmit={handleSubmit}>
                        {!isLogin && (
                            <div className="mb-3">
                                <label className="form-label text-muted small fw-bold">Nome de Usuário</label>
                                <input 
                                    type="text" 
                                    className="form-control" 
                                    value={nome}
                                    onChange={e => setNome(e.target.value)} 
                                    required={!isLogin} 
                                />
                            </div>
                        )}

                        <div className="mb-3">
                            <label className="form-label text-muted small fw-bold">E-mail</label>
                            <input 
                                type="email" 
                                className="form-control" 
                                value={email}
                                onChange={e => setEmail(e.target.value)} 
                                required 
                            />
                        </div>

                        <div className="mb-4">
                            <label className="form-label text-muted small fw-bold">Senha</label>
                            <input 
                                type="password" 
                                className="form-control" 
                                value={senha}
                                onChange={e => setSenha(e.target.value)} 
                                required 
                            />
                            {!isLogin && (
                                <div className="form-text text-muted" style={{ fontSize: '0.75rem' }}>
                                    Obrigatório: Mínimo de 8 caracteres, contendo pelo menos uma letra maiúscula, uma minúscula e um número.
                                </div>
                            )}
                        </div>

                        <button 
                            type="submit" 
                            className="btn btn-primary w-100 fw-bold mb-3"
                            disabled={carregando}
                        >
                            {carregando ? 'Processando...' : (isLogin ? 'Entrar' : 'Cadastrar')}
                        </button>

                        <div className="text-center">
                            <button 
                                type="button" 
                                className="btn btn-link text-decoration-none small"
                                onClick={() => {
                                    setIsLogin(!isLogin);
                                    setErro('');
                                    setSucesso('');
                                }}
                            >
                                {isLogin 
                                    ? 'Ainda não tem conta? Cadastre-se' 
                                    : 'Já possui uma conta? Faça Login'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}