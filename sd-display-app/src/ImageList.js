import * as React from "react";
import "@cloudscape-design/global-styles/index.css"
import Grid from "@cloudscape-design/components/grid"
import ImageBig from "./ImageBig";

const shuffleArray = (array) => {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

const randomDirection = () => Math.random() < 0.5

export default ({ images }) => {
    const [imageList, setImages] = React.useState([...images]);
    const [currentIndex, setCurrentIndex] = React.useState(0)
    const [imgLef, setImgLef] = React.useState(null)
    const [imgRight, setImgRight] = React.useState(null)
    const [direction, setDirection] = React.useState(false)
    const imagesRef = React.useRef(imageList);
    const indexRef = React.useRef(currentIndex);
    //var imageList = []

    const changeImages = () => {

        let newIndex = (indexRef.current + 1) % imagesRef.current.length
        let par = newIndex % 2
        if (par == 0) setImgLef(imagesRef.current[newIndex])
        else setImgRight(imagesRef.current[newIndex])
        indexRef.current = newIndex
    }

    React.useEffect(() => {
        const arr = shuffleArray(images)
        imagesRef.current = arr
        if (arr.length > 0) setImgLef(arr[0])
        if (arr.length > 1) setImgRight(arr[1])
        setDirection(randomDirection())
        //if (images.length >0 ) images[0]['qr'].then(val => console.log(val) )
    }, [images]);


    React.useEffect(() => {
        const intervalId = setInterval(changeImages, 15000)
        return () => { clearInterval(intervalId) }
    }, [])

    return (

        <Grid
            disableGutters
            gridDefinition={[{ colspan: { xxs: 6 } }, { colspan: { xxs: 6 } }]}
        >
            {imgLef ? <ImageBig key={0} im={imgLef} direction={direction}  position= {"left"}/> : <div />}
            {imgRight ? <ImageBig key={1} im={imgRight} direction={!direction} position= {"right"}/> : <div />}
        </Grid>
    )

}




