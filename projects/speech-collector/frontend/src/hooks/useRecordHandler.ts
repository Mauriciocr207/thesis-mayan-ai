import { useEffect, useState } from "react"

type Record = {
    complete: boolean;
    file: Blob | null;
}

export default function useRecordHandler(frases: string[]) {
    const [records, setRecords] = useState<Record[]>([])

    useEffect(() => {
        setRecords(Array.from({ length: frases.length }).map(() => ({
            complete: false,
            file: null
        })))
    }, [frases]);

    function setFileToRecord(index: number, file: Blob | null) {
        setRecords((prevRecords) => {
            prevRecords[index] = {
                ...prevRecords[index],
                file
            }

            return prevRecords
        })
    }

  return {
    records,
    setFileToRecord,
  };
}
