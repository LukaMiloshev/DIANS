import React, { useState, useEffect } from "react";
import axios from "axios";
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './Home';
import List from './List';


function App() {
    const [books, setBooks] = useState([]);

    useEffect(() => {
        axios.get("http://localhost:8080/api/all")
            .then(response => {
                setBooks(response.data);
            })
            .catch(error => {
                console.error("There was an error fetching the books!", error);
            });
    }, []);

    return (
        <div className="App">
            <h1>Books</h1>
            <ul>
                {books.map(book => (
                    <li key={book.id}>
                        {book.title} - {book.isbn}
                    </li>
                ))}
            </ul>
        </div>
    );
    const App = () => {
        return (
            <Router>
                <Routes>
                    <Route exact path="/" element={<Home />} />
                    <Route path="/list" exact element={<List />} />  {/* Патека за листата */}
                </Routes>
            </Router>
        );
    };
}

export default App;

