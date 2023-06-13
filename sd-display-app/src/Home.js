import * as React from "react";
import "@cloudscape-design/global-styles/index.css"
import Grid from "@cloudscape-design/components/grid"
import Modal from "@cloudscape-design/components/modal";


import APIS from "./apis.js"
import ImageList from "./ImageList.js";




export default () => {
    const [images, setImages] = React.useState([]);
    const [visible, setVisible] = React.useState(false)
    const [image, setImage] = React.useState({'url':''})
    const checkSocket = (socket) => {
        socket.send(JSON.stringify({ action: 'onmessage', data: 'Hola' }))
    }

    const fetchImages  = () => {
        fetch(APIS.images)
            .then((response) => response.json())
            .then((data) => {
                setImages(data.items)
            });
    }


    React.useEffect(() => {

        fetchImages()

        const socket = new WebSocket(APIS.socket);


        // Event handler for WebSocket open
        socket.onopen = () => {
            console.log('WebSocket connection established.')
            socket.send(JSON.stringify({ action: 'onmessage', data: 'Hola' }))

        };

        // Event handler for WebSocket message
        socket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            console.log('Received message from server:', message);

            if ('url' in message) {
                setImage({...message})
                setVisible(true)
                fetchImages()
                setTimeout(()=>{setVisible(false)}, 10000)
            }
        };

        // Event handler for WebSocket close
        socket.onclose = (event) => {
            console.log('WebSocket connection closed with code:', event.code);
        };

        // Event handler for WebSocket error
        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
        const intervalId = setInterval(checkSocket, 15000, socket)
        return () => { clearInterval(intervalId); socket.close() }


    }, []);


    return (<div>
        <Grid key={2}
            disableGutters
            gridDefinition={[

                { colspan: { xxs: 12 } },

            ]}
        >

            <ImageList images={images} />

        </Grid>
        <Modal
            header={<div/>}
            size="large"
            closeAriaLabel={""}
            visible={visible} >
                <div className={"new-image"}><img id="new-image" src={image.url} /></div>
        </Modal>

    </div>
    )

}




