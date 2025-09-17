import React, {useState} from "react";

function App() {
    const [userQuery, setUserQuery] = useState('');
    const updateUserQuery = event => {
        setUserQuery(event.target.value);
        console.log("userQuery", userQuery);
    }
    const searchQuery = () => {
        window.open(`https://google.com/search?q=${userQuery}`);
    }
    const handleKeyPress = event => {
        if (event.key === "Enter") {
            searchQuery();
        }
    }
    return (
        <div className="App">
            <p>
                This is the app.
            </p>
            <input value={userQuery} onChange={updateUserQuery}/>
            <button onClick={searchQuery} onChange={updateUserQuery} onKeyPress={handleKeyPress}>Search</button>
            <hr />
            <apify_sherlock />
        </div>
    );
}

export default App;
