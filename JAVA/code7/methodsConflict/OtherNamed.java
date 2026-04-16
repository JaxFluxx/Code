package methodsConflict;

public interface OtherNamed
{
//	String getName();
	default String getName()
	{return "this is the method in OtherNamed interface.";}
}
