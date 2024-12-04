import React, { useState, useEffect } from 'react';

const List = () => {
    const [state, setState] = useState([]);

    useEffect(() => {
        fetch('http://localhost:8080/api/all')  // Патеката до вашето API за добивање на сите записи
            .then(response => response.json())
            .then(data => {
                setState(data);
            });
    }, []);  // Empty dependency array за да се повика само при првото рендерирање

    return (
        <div>
            {state.map(obj => (
                <div key={obj.id}>
                    {obj.title}  {/* Прикажете ги атрибутите што ги имате во објектот */}
                </div>
            ))}
        </div>
    );
};

export default List;
