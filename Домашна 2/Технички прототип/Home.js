import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
    return (
        <div>
            <h1>Welcome to Book App</h1>
            <Link to="/list">See list</Link>  {/* Кликни за да се однесеш на листата */}
        </div>
    );
};

export default Home;
