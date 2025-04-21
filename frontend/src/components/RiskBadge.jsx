import React from "react";
const colors = { High: "text-red-600", Medium: "text-yellow-500", Low: "text-green-600" };
export default function RiskBadge({ level }) { return <span className={`font-semibold ${colors[level]}`}>{level}</span>; }