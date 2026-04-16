package methodsConflict;

public interface Named
{
	String getName();
//	default String getName()
//	{return "this is the method in Named interface.";}
}
