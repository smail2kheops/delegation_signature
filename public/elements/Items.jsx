import {Card, CardContent, CardHeader} from "@/components/ui/card"
import {Skeleton} from "@/components/ui/skeleton"
import {ScrollArea} from "@/components/ui/scroll-area"
import {Input} from "@/components/ui/input"
import {Button} from "@/components/ui/button"
import {Badge} from "@/components/ui/badge"
import {useState} from 'react';
import {Accordion, AccordionContent, AccordionItem, AccordionTrigger} from "@/components/ui/accordion"

const Header = ({title, date}) => {
    return (<CardHeader className="flex flex-row items-center justify-between">
        <div className="font-semibold">{title || '?'}</div>
    </CardHeader>);
};

const ItemCard = ({props}) => {
    return (
        <>
            <div key={props} className="text-sm hover:bg-accent p-2">
                <span className="text-[12px]">{props}</span>
            </div>
        </>
    );
};

const Categorizer = ({items}) => {

    const categorizedData = items.reduce((acc, curr) => {
        const {text, theme} = curr;

        if (!acc[theme]) {
            acc[theme] = {
                items: [],
            };
        }
        acc[theme].items.push(text);

        return acc;
    }, {});

    return (
        <>
            {Object.keys(categorizedData).map((key, index) => (
                <Accordion type="single" collapsible>
                    <AccordionItem value={key}>
                        <AccordionTrigger>
                            <div className="flex flex-row items-center justify-between w-full mr-2">
                                <span>{key}</span>
                                <Badge vvariant="secondary">{categorizedData[key]?.items?.length}</Badge>
                            </div>
                        </AccordionTrigger>
                        <AccordionContent>
                            <div className="border-t">{
                                categorizedData[key]?.items?.map((item, itemIndex) => (
                                    <ItemCard props={item}/>
                                ))
                            }</div>
                        </AccordionContent>
                    </AccordionItem>
                </Accordion>
            ))}
        </>
    );
}

const Items = ({items}) => {
    const [searchQuery, setSearchQuery] = useState('');

    const filteredTexts = props.items.filter((item) =>
        item.text.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="flex flex-col align-center overflow-hidden border-0 h-full w-full">
            <div className="flex items-center border-0  w-full overflow-hidden">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
                     viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" stroke-width="2" stroke-linecap="round"
                     stroke-linejoin="round"
                     className="lucide lucide-search ml-2 mr-2 h-4 w-25 shrink-0 opacity-50 ">
                    <circle cx="11" cy="11" r="8"></circle>
                    <path d="m21 21-4.3-4.3"></path>
                </svg>
                <Input
                    placeholder='recherche'
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    class="rounded-0 border-l h-11 p-2 w-[90%] outline-none bg-background"
                />
            </div>
            <ScrollArea className="h-[400px] w-full  border-0 border-t">
                <div className='h-50 flex flex-col space-y-3'>
                    <div className="p-4 space-y-2">
                        {<Categorizer items={filteredTexts}/>}
                    </div>
                </div>
            </ScrollArea>
        </div>
    )
        ;
};

const SkeletonCard = () => {
    const tags = [1, 2, 3]
    return (
        <div className="flex flex-col align-center overflow-hidden border-0 h-full w-full">
            <div className="flex items-center border-0  w-full overflow-hidden">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
                     viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" stroke-width="2" stroke-linecap="round"
                     stroke-linejoin="round"
                     className="lucide lucide-search ml-2 mr-2 h-4 w-25 shrink-0 opacity-50 ">
                    <circle cx="11" cy="11" r="8"></circle>
                    <path d="m21 21-4.3-4.3"></path>
                </svg>
                <Input
                    placeholder='recherche'
                    class="rounded-0 border-l h-11 p-2 w-[90%] outline-none opacity-50 "
                />
            </div>
            <ScrollArea className="h-[400px] w-full  border-0 border-t">
                <div className='h-50 flex flex-col space-y-3'>
                    <div className="p-4 space-y-2">
                        {tags.map((tag) => (
                            <>
                                <Accordion type="single" collapsible>
                                    <AccordionItem key={tag}>
                                        <AccordionTrigger><Button className='w-full bg-white hover:bg-white'><Skeleton className="h-full w-full rounded-full"/></Button></AccordionTrigger>
                                        <AccordionContent>
                                               <Skeleton className="w-100"/>
                                               <Skeleton className="w-100"/>
                                               <Skeleton className="w-100"/>
                                        </AccordionContent>
                                    </AccordionItem>
                                </Accordion>
                            </>
                        ))}
                    </div>
                </div>
            </ScrollArea>
        </div>

    )
        ;
};

const EmptyCard = () => {
    return (
        <Card>
            <div className="flex flex-col align-center overflow-hidden border-0 h-full w-full">
                <div className="flex items-center border-0  w-full overflow-hidden">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
                         viewBox="0 0 24 24" fill="none"
                         stroke="currentColor" stroke-width="2" stroke-linecap="round"
                         stroke-linejoin="round"
                         className="lucide lucide-search ml-2 mr-2 h-4 w-25 shrink-0 opacity-50 ">
                        <circle cx="11" cy="11" r="8"></circle>
                        <path d="m21 21-4.3-4.3"></path>
                    </svg>
                    <Input
                        placeholder='recherche'
                        value=''
                        class="rounded-0 border-l h-11 p-2 w-[90%] outline-none bg-background"
                        disabled
                    />
                </div>
                <ScrollArea className="h-[400px] w-full  border-0 border-t">
                    <div className="h-[22px] w-full p-2 "><span className="text-gray font-weight-bold">0 Résultats Trouvés</span></div>
                </ScrollArea>
            </div>
        </Card>
    );
};

export default function SourcesCard() {
    return (

        <div className="h-75 space-y-4">
            {props.status == 'progress' ?
                (
                    <Card>
                        <SkeletonCard/>
                    </Card>
                )
                :
                (
                    props.items.length == 0 ?
                        (<EmptyCard/>)
                        :
                        (
                            <Card>
                                <Items items={props.items}/>
                            </Card>
                        )
                )
            }
        </div>

    );
}