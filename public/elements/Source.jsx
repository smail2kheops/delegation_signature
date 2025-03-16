import {Card, CardContent, CardHeader} from "@/components/ui/card"
import {Input} from "@/components/ui/input"
import {Label} from "@/components/ui/label"
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue,} from "@/components/ui/select"
import {Button} from "@/components/ui/button"
import {Dialog, DialogContent, DialogTitle, DialogTrigger,} from "@/components/ui/dialog"
import {Skeleton} from "@/components/ui/skeleton"
import {Badge} from "@/components/ui/badge"
import {Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger,} from "@/components/ui/sheet"
import {Separator} from "@/components/ui/separator"
import {Tooltip, TooltipContent, TooltipProvider, TooltipTrigger,} from "@/components/ui/tooltip"

const Header = ({title}) => {
    return (<CardHeader className="flex flex-row items-center justify-between w-full">
        <div className="font-semibold">{title || '?'}</div>
        {/*<Badge variant="secondary">{type || '?'}</Badge>*/}
    </CardHeader>);
};


const ResultHeader = ({title, type, feedback}) => {
    return (<CardHeader className="flex flex-row items-center justify-between w-full">
        <div className="font-semibold">{title || '?'}</div>
        <Stats type={type} feedback={feedback}/>
    </CardHeader>);
};

const Neutre = ({value}) => {
    return (
        <>
            <TooltipProvider>
                <Tooltip>
                    <TooltipTrigger asChild>
                        <Button variant="none">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                 fill="none"
                                 transform="rotate(-90)"
                                 stroke="gray" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                                 className="lucide lucide-thumbs-up h-4 w-4">
                                <path d="M7 10v12"></path>
                                <path
                                    d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2a3.13 3.13 0 0 1 3 3.88Z"></path>
                            </svg>
                            <Badge variant="success">{value}%</Badge>
                        </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                        <p>Neutre</p>
                    </TooltipContent>
                </Tooltip>
            </TooltipProvider>
        </>
    )
        ;
};

const Positif = ({value}) => {
    return (
        <>
            <TooltipProvider>
                <Tooltip>
                    <TooltipTrigger asChild>
                        <Button variant="none">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                 fill="none"
                                 stroke="green" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                                 className="lucide lucide-thumbs-up h-4 w-4">
                                <path d="M7 10v12"></path>
                                <path
                                    d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2a3.13 3.13 0 0 1 3 3.88Z"></path>
                            </svg>
                            <Badge variant="success">{value}%</Badge>
                        </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                        <p>Pour</p>
                    </TooltipContent>
                </Tooltip>
            </TooltipProvider>
        </>
    )
        ;
};

const Stats = ({type, feedback}) => {
    const status = {
        'cached': 'depuis le cache',
        'generated': "generer par l'IA",
    }
    const test = 'cached'
    let total = feedback['0'] + feedback['1'] + feedback['2']
    if (total == 0)
        total = 1
    const pos = parseInt(feedback['1'] * 100 / total, 10)
    const neu = parseInt(feedback['2'] * 100 / total, 10)
    const neg = 100 - pos - neu
    return (
        <div className="flex flex-row h-5 items-center space-x-2">

            {
                test == 'cached' ?
                    <>
                        <Positif value={pos}/>
                        <Separator orientation="vertical"/>
                        <Neutre value={neu}/>
                        <Separator orientation="vertical"/>
                        <Negatif value={neg}/>
                        <Separator orientation="vertical"/>
                    </>
                    :
                    <></>
            }

            <Badge variant="neutre">{status[type] || "generer par l'IA"}</Badge>
        </div>
    )
};

const Negatif = ({value}) => {
    return (
        <>
            <TooltipProvider>
                <Tooltip>
                    <TooltipTrigger asChild>
                        <Button variant="none">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                 fill="none"
                                 stroke="red" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                                 className="lucide lucide-thumbs-down h-4 w-4">
                                <path d="M17 14V2"></path>
                                <path
                                    d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22a3.13 3.13 0 0 1-3-3.88Z"></path>
                            </svg>
                            <Badge variant="failed">{value}%</Badge>
                        </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                        <p>Contre</p>
                    </TooltipContent>
                </Tooltip>
            </TooltipProvider>
        </>
    );
};

const SourceCard = ({props}) => {
    return (<Card className="overflow-y-auto h-full w-full">
        <Header title={props.Numero.toUpperCase()}/>
        <CardContent className="flex flex-col gap-2">
            <CardContent>
                <form>
                    <div className="grid w-full items-center gap-4">
                    <div className="flex flex-col space-y-1.5">
                            <Label htmlFor="name">Signataire</Label>
                            <Input id="name" value={props.Signataire} disabled/>
                        </div>
                        <div className="flex flex-col space-y-1.5">
                            <Label htmlFor="name">Fonction</Label>
                            <Input id="name" value={props.Fonction} disabled/>
                        </div>
                        <div className="flex flex-col space-y-1.5">
                            <Label htmlFor="name">Direction</Label>
                            <Input id="name" value={props['Direction DGA']} disabled/>
                        </div>
                        <div className="flex flex-col space-y-1.5">
                            <Label htmlFor="name"> </Label>
                            <Select>
                                <SelectTrigger id="framework">
                                    <SelectValue placeholder="Suppleants"/>
                                </SelectTrigger>
                                <SelectContent side="top">
                                    {props.Suppleant.map(value => (<SelectItem value={value}>{value}</SelectItem>))}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="flex flex-col space-y-1.5">
                            <Button>
                                <a className='w-full' href={'mailto:' + props.information.email}>Demander le bon de commande</a>
                            </Button>
                        </div>
                        <Dialog>
                            <DialogTrigger asChild><Button>Ouvrir Source</Button></DialogTrigger>
                            <div width="800" height="600"><DialogContent className="flex  flex-col w-full h-full">
                                <DialogTitle>Source</DialogTitle>
                                <iframe
                                    src={props.path}
                                    height="100%"
                                />
                            </DialogContent></div>
                        </Dialog>
                    </div>
                </form>
            </CardContent>
        </CardContent>
    </Card>);
};

const SkeletonCard = () => {
    return (<Card className="overflow-y-auto h-full">
        <div className="space-y-1.5 p-6 flex flex-row items-center justify-between">
            <Skeleton className="h-[22px] w-[150px] rounded-xl"/>
        </div>
        <CardContent className="flex flex-col gap-2">
            <CardContent>
                <form>
                    <div className="grid w-full items-center gap-4">
                        <div className="flex flex-col space-y-1.5">
                            <Skeleton className="h-4 w-20 rounded-xl"/>
                            <Skeleton className="h-10 w-full rounded-xl"/>
                        </div>
                        <div className="flex flex-col space-y-1.5">
                            <Skeleton className="h-4 w-20 rounded-xl"/>
                            <Skeleton className="h-10 w-full rounded-xl"/>
                        </div>
                        <div className="flex flex-col space-y-1.5">
                            <Skeleton className="h-4 w-20 rounded-xl"/>
                            <Skeleton className="h-10 w-full rounded-xl"/>
                        </div>
                        <div className="flex flex-col space-y-1.5">
                            <Skeleton className="h-4 w-0 rounded-xl"/>
                            <Skeleton className="h-10 w-full rounded-xl"/>
                        </div>
                        <div className="flex flex-col space-y-1.5">
                            <Skeleton className="h-10 w-full rounded-xl"/>
                        </div>
                        <div className="flex flex-col space-y-1.5">
                            <Skeleton className="h-10 w-full rounded-xl"/>
                        </div>
                    </div>
                </form>
            </CardContent>
        </CardContent>
    </Card>);
};

const EmptyCard = () => {
    return (<Card className="overflow-y-auto h-full">
        <Header title="Pas De Resultat"/>
        <CardContent className="flex flex-col gap-2">
            Aucun signataire trouvé. Veuillez reposer votre question avec plus de clarté.
        </CardContent>
    </Card>);
};

const Explication = ({question, message}) => {
    return (
        <Sheet>
            <SheetTrigger><Button variant="outline">Explication</Button></SheetTrigger>
            <SheetContent>
                <SheetHeader>
                    <SheetTitle>Explication</SheetTitle>
                    <div className="flex flex-col space-y-1.5  font-semibold">
                        {question}
                    </div>
                    <div className="flex flex-col space-y-1.5">
                        {message}
                    </div>
                </SheetHeader>
            </SheetContent>
        </Sheet>
    )
};

const ExplicationDialog = ({question, message}) => {
    return (
        <Dialog>
            <DialogTrigger asChild><Button className="max-w-[70%]">Explication choix de la
                direction</Button></DialogTrigger>
            <DialogContent className="flex flex-col">
                <DialogTitle>Explication</DialogTitle>
                <div className="flex flex-col space-y-1.5 font-semibold">
                    {question}
                </div>
                <div className="flex flex-col space-y-1.5">
                    {message}
                </div>
            </DialogContent>
        </Dialog>
    )
};

export default function SourcesCard() {
    console.log(props);
    return (
        <div className="space-y-4">
            {props.status == 'progress' ?
                (<SkeletonCard/>)
                :
                (
                    props.sources.length == 0 ?
                        (<EmptyCard/>)
                        :
                        (
                            <div className='w-full flex flex-col space-y-4 items-center'>

                                <Card className="w-full p-4 flex flex-col items-center justify-between space-y-4">
                                    {/*<ResultHeader title="Résultat de la recherche." type={props.source} feedback={props.feedback}/>*/}
                                    {props.sources.map(source => (<SourceCard props={source}/>))}
                                    <ExplicationDialog question={props.question} message={props.explication}/>
                                </Card>
                            </div>
                        )
                )
            }
        </div>);
}