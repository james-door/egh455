import React from "react";

function getDateFromUNIXTime(unixTime) {

    const date = new Date(unixTime * 1000); 
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();

    let hours = date.getHours();
    const minutes = date.getMinutes().toString().padStart(2, '0'); 
    const seconds = date.getSeconds().toString().padStart(2, '0'); 
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12 || 12; 

    const formattedDateTime = `${day}/${month}/${year} ${hours}:${minutes}:${seconds} ${ampm}`;
    return formattedDateTime;
}

export default function DataTable({data})
{
    return (
      <div className="datatable-style">
    <div className="table-container">
        <table>
            <thead>
                <tr className="columnlabel">
                    <th>Time</th>
                    <th>Pressure</th>
                    <th>Humidity</th>
                    <th>Temperature</th>
                    <th>Light</th>
                    <th>Reducing</th>
                    <th>Oxidising</th>
                    <th>Ammonia</th>
                    <th>Detections</th>
                </tr>
            </thead>
            <tbody className="row-style">
                {data.map((val, key) => (
                    <tr key={key}>
                        <td>{getDateFromUNIXTime(val.unix_time)}</td>
                        <td>{Math.round(val.pressure)}</td>
                        <td>{val.humidity}</td>
                        <td>{Math.round(val.temperature)}</td>
                        <td>{Math.round(val.light)}</td>
                        <td>{Math.round(val.reducing)}</td>
                        <td>{Math.round(val.oxidising)}</td>
                        <td>{Math.round(val.ammonia)}</td>
                        <td>{val.detections == null ? "-" : val.detections}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    </div>
</div>

    );
}