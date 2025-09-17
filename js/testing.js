let tree = 12;
console.log(tree)
for (let i = 10; i > 0; i--) {
    console.log(i)
}

function dedw(p1, callback) {
    console.log(p1)
    callback()
}

function dedw2() {
    console.log("im ded!")
}

const dedw3 = () => console.log("im ded3!")

dedw(100, dedw2)
dedw3()

dedw3 == "im ded3!" ? console.log(true) : console.log(false)

console.log(1===true)

fetch('https://jsonplaceholder.typicode.com/posts')
    .then(response => response.json())
    .then(data => data.forEach(element => console.log('\n',element.id, element.userId,':',element.title, '\n',element.body)
    ));






