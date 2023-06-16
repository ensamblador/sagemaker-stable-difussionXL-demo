import * as React from "react";
import "@cloudscape-design/global-styles/index.css"
import Grid from "@cloudscape-design/components/grid"
import Modal from "@cloudscape-design/components/modal";
import { generateQR } from "./utils.js";

import APIS from "./apis.js"
import ImageList from "./ImageList.js";
import NewImage from "./NewImage.js";



export default () => {
    const [images, setImages] = React.useState([]);
    const [visible, setVisible] = React.useState(false)
    const [image, setImage] = React.useState({
        'url': '',
        'qr': generateQR('foo')
    })
    const checkSocket = (socket) => {
        socket.send(JSON.stringify({ action: 'onmessage', data: 'Hola' }))
    }
    var timeoutId = null

    const fetchImages = () => {
        fetch(APIS.images)
            .then((response) => response.json())
            .then((data) => {
                const itemsWithQR = data.items.map(item => {

                    item['qr'] = generateQR(item['url'])

                    return item
                })
                //console.table(itemsWithQR)
                setImages(itemsWithQR)
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
                if (message['resolution'] == 'low') {

                    if (timeoutId) {
                        clearTimeout(timeoutId)
                    }
                    message['qr'] = generateQR(message['url'])
                    setImage({ ...message })
                    setVisible(true)
                    fetchImages()
                    timeoutId = setTimeout(() => { setVisible(false) }, 45000)
                }
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
         onDismiss={() => setVisible(false)}
            header={<div />}
            size="large"
            closeAriaLabel={""}
            visible={visible} >
            <NewImage im={image} />
        </Modal>

    </div>
    )

}




