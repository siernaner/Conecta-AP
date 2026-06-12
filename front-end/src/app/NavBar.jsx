"use client";
import { useState, useContext } from 'react';
import Link from 'next/link';
import { AuthContext } from '../contexts/AuthContext';

export default function NavBar() {
    const { user, signOut } = useContext(AuthContext);
    const [isOpen, setIsOpen] = useState(false);

    const footerLinks = [
        { href: "/sobre", label: "Sobre o Projeto", icon: "bi-info-circle" },
        { href: "/disclaimer", label: "Aviso Legal", icon: "bi-shield-exclamation" },
        { href: "/contato", label: "Contato", icon: "bi-envelope" }
    ];

    return (
        <>
            <nav className="navbar navbar-dark bg-dark shadow-sm py-2 fixed-top">
                <div className="container d-flex align-items-center justify-content-between">
                    <div className="d-flex align-items-center">
                        <button className="btn btn-dark border-0 me-2" onClick={() => setIsOpen(true)}>
                            <i className="bi bi-list fs-3"></i>
                        </button>
                        {user && (
                            <span className="text-light d-none d-md-inline-block small border-start border-secondary ps-3 ms-2">
                                Olá, <span className="text-light fw-bold">{user.nome}</span>
                            </span>
                        )}
                    </div>

                    <Link href="/" className="navbar-brand fw-bold text-center d-none d-sm-block">
                        Conecta Alta Paulista
                    </Link>

                    <div className="d-flex align-items-center">
                        {user ? (
                            <button onClick={signOut} className="btn btn-sm btn-outline-danger fw-bold rounded-pill px-3">
                                Sair
                            </button>
                        ) : (
                            <Link href="/login" className="btn btn-sm btn-primary fw-bold rounded-pill px-3">
                                Entrar / Cadastrar
                            </Link>
                        )}
                    </div>
                </div>
            </nav>

            <div style={{ height: '56px' }}></div> {/* compensar header fixo */}

            <div className={`offcanvas offcanvas-start ${isOpen ? 'show' : ''}`} 
                 style={{visibility: isOpen ? 'visible' : 'hidden', backgroundColor: '#141414', color: 'white', width: '280px'}}>
                <div className="offcanvas-header border-bottom border-secondary">
                    <h5 className="offcanvas-title fw-bold text-primary">Menu</h5>
                    <button onClick={() => setIsOpen(false)} className="btn-close btn-close-white"></button>
                </div>
                <div className="offcanvas-body">
                    <ul className="list-unstyled">
                        <li className="mb-4">
                            <Link href="/" className="text-decoration-none text-light fs-5" onClick={() => setIsOpen(false)}>
                                <i className="bi bi-house-door me-3"></i>Início
                            </Link>
                        </li>
                        {user?.role === 'admin' && (
                            <>
                                <div className="text-light small fw-bold mb-3 mt-4 text-uppercase">Administração</div>
                                <li className="mb-3">
                                    <Link href="/admin/usuarios" className="text-decoration-none text-light" onClick={() => setIsOpen(false)}>
                                        <i className="bi bi-people me-3"></i>Gestão de Usuários
                                    </Link>
                                </li>
                                <li className="mb-3">
                                    <Link href="/admin/fontes" className="text-decoration-none text-light" onClick={() => setIsOpen(false)}>
                                        <i className="bi bi-hdd-network me-3"></i>Fontes e Cidades
                                    </Link>
                                </li>
                                <li className="mb-3">
                                    <Link href="/admin/moderacao" className="text-decoration-none text-light" onClick={() => setIsOpen(false)}>
                                        <i className="bi bi-shield-check me-3"></i>Moderação de Notícias
                                    </Link>
                                </li>
                                <div className="dropdown-divider my-3" style={{borderTop: '1px solid #444'}}></div>
                            </>
                        )}
                        <div className="text-light small fw-bold mb-3 mt-4 text-uppercase">Informações</div>
                        {footerLinks.map((link, idx) => (
                            <li key={idx} className="mb-3">
                                <Link href={link.href} className="text-decoration-none text-light" onClick={() => setIsOpen(false)}>
                                    <i className={`bi ${link.icon} me-3`}></i>{link.label}
                                </Link>
                            </li>
                        ))}
                        {user && user.role !== 'admin' && (
                            <li className="mt-3">
                                <Link href="/perfil" className="text-decoration-none text-light" onClick={() => setIsOpen(false)}>
                                    <i className="bi bi-person me-3"></i>Meu Perfil
                                </Link>
                            </li>
                        )}
                    </ul>
                </div>
            </div>
            {isOpen && <div className="offcanvas-backdrop fade show" onClick={() => setIsOpen(false)}></div>}
        </>
    );
}