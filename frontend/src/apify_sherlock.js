import React, {useEffect, useState} from "react";

function sherlock() {
    useEffect(() => {
        const [data, setdata] = useState({});
        fetch('')
            .then(response => response.json())
            .then(json => {
                    console.log("data", json);
                }
            );

    }, []);

    const {setup, punchline} = sherlock


    return (
        <div>
            <h3>Sherlock</h3>
        </div>
    )
}

export default sherlock;