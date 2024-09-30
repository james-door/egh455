import React from "react";
import { useLocation, Link} from 'react-router-dom';



export default function NavBar(props)
{
    const location = decodeURI(useLocation().pathname).substring(1)
    
    const pathNames = ["Air Quality", "Identified Targets", "Video Feed", "Data Log"]

    const buttons = pathNames.map((path) => {
        const buttonStatus = (path === location) ? "active" : "inactive";
        return(
            <Link to={`/${path}`}>
                <button className={buttonStatus} key={path}>{path}</button>
            </Link>
        );
      });


    return (
    <div className="navbar-style">
        {buttons}
    </div>)
}