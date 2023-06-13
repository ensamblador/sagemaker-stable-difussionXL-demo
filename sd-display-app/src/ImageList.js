import * as React from "react";
import "@cloudscape-design/global-styles/index.css"
import Grid from "@cloudscape-design/components/grid"


const shuffleArray = (array) => {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

const randomDirection = () => Math.random() < 0.5

const ImageBigLeft = ({ im, direction }) => {
    React.useEffect(() => {
        const imgElement = document.getElementById('left-image')
        if (direction) {
            imgElement.style.top = "-50px"
        } else {
            imgElement.style.top = "0px"
        }

    },[im])
    return (<div className={"single-image-" + im.resolution + (direction ? " down" : " up")}><img id="left-image" src={im.url} /></div>)
}

const ImageBigRight = ({ im, direction }) => {
    React.useEffect(() => {
        const imgElement = document.getElementById('right-image')
        if (direction) {
            imgElement.style.top = "-50px"
        } else {
            imgElement.style.top = "0px"
        }

    },[im])
    return (<div className={"single-image-" + im.resolution + (direction ? " down" : " up")}><img id="right-image" src={im.url} /></div>)
}
   
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
        //console.log(imagesRef.current, currentIndex, newIndex, par, imagesRef.current.length)
        if (par == 0) setImgLef(imagesRef.current[newIndex])
        else setImgRight(imagesRef.current[newIndex])
        //setCurrentIndex(oldIndex => newIndex)
        indexRef.current = newIndex
    }

    React.useEffect(() => {
        //console.log("use effect")
        const arr = shuffleArray(images)
        //imageList = arr

        //setImages(preImages => [...arr])
        imagesRef.current = arr
        //console.log(imagesRef)
        if (arr.length > 0) setImgLef(arr[0])
        if (arr.length > 1) setImgRight(arr[1])
        setDirection(randomDirection())
        //let myimageList = imageList
        //const intervalId = setInterval(()=>{console.log(myimageList)}, 5000)
        //return () => { clearInterval(intervalId)}
    }, [images]);

    //const intervalId = setInterval(()=>{console.log(imageList)}, 5000)

    React.useEffect(() => {
        //console.log("Set Interval")
        const intervalId = setInterval(changeImages, 15000)
        return () => { clearInterval(intervalId) }
    }, [])

    return (

        <Grid
            disableGutters
            gridDefinition={[{ colspan: { xxs: 6 } }, { colspan: { xxs: 6 } }]}
        >
            {imgLef ? <ImageBigLeft key={0} im={imgLef} direction={direction} /> : <div />}
            {imgRight ? <ImageBigRight key={1} im={imgRight} direction={!direction} /> : <div />}
        </Grid>
    )

}




