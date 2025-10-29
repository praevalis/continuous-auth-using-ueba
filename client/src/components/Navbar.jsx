import { BsFileEarmarkLock2 } from "react-icons/bs";

const Navbar = () => {
    return (
        <nav className="flex w-full px-40 py-6">
            <div className="flex items-center gap-2">
                <BsFileEarmarkLock2 className="text-3xl text-blue-400" />
                <h3 className="text-xl text-blue-400">
                    <strong>UEBA</strong>
                </h3>
            </div>
        </nav>
    );
};

export default Navbar;
