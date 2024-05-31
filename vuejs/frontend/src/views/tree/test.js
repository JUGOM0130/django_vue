let data =[
        {
            id: "1",
            content:"ALD-A0001Z000",
            child: [
                {
                    id: "2",
                    content:"CND-AA002Z000",
                    child: [
                    {
                    id: "5",
                    content:"CLA-A0002Z000",
                    child: [
    
                    ]
                }
                    ]
                }
            ],
        }, {
            id: "3",
            content:"ZQD-A0001Z000",
            child: [
                {
                    id: "4",
                    content:"ALD-A0002Z000",
                    child: [
    
                    ]
                }
            ]
        }
    ];

function find(child,find_item){
    let object = child;
    for(let i=0; i<object.length; i++){
        if(object[i].id==find_item){
            console.log(object)
        }
    }
    find(object.find,find_item)
}
console.log(data)
console.log(find(data,"4"))